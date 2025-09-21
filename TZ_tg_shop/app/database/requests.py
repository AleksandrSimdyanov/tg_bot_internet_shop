from app.database.models import Type, async_session, Product, Cart, Order, OrderCart, Appeal, User
from sqlalchemy import select
from sqlalchemy import select, delete, update

async def get_types():
    async with async_session() as session:
        types = await session.scalars(select(Type))
    return types


async def get_products(type_id):
    async with async_session() as session:
        products = await session.scalars(select(Product).where(Product.type_id == type_id))
    return products


async def get_product_by_id(product_id):
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
    return product


async def get_type_by_id(type_id):
    async with async_session() as session:
        type = await session.scalar(select(Type).where(Type.id == type_id))
    return type


async def get_cart_by_id(cart_id):
    async with async_session() as session:
        cart = await session.scalar(select(Cart).where(Cart.id == cart_id))
    return cart


async def add_cart(user_id, product_id, quantity=1):
    async with async_session() as session:
        cart = await session.scalar(select(Cart).where(Cart.user_id == user_id,
                                                       Cart.product_id == product_id,
                                                       Cart.status == "new"))
        if cart is None:
            cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            session.add(cart)
        else:
            cart.quantity += 1
        await session.commit()
        await session.refresh(cart)
    return cart.quantity


async def remove_cart(user_id, product_id):
    async with async_session() as session:
        cart = await session.scalar(select(Cart).where(Cart.user_id == user_id,
                                                       Cart.product_id == product_id,
                                                       Cart.status == "new"))
        if cart:
            if cart.quantity > 0:
                cart.quantity -= 1
                if cart.quantity == 0:
                    await session.delete(cart)  # Удаляем позицию, если количество стало равно 0
                    return 0
            else:
                return 0  # Уже ничего не остаётся в корзине
        else:
            return 0  # Продукт изначально отсутствовал в корзине
        await session.commit()
        await session.refresh(cart)
        return cart.quantity


async def get_carts_by_user_id(user_id):
    async with async_session() as session:
        stmt = await session.scalars(select(Cart).where(Cart.user_id == user_id, Cart.status == "new"))
    return stmt


async def get_sum_cart_by_user_id(user_id):
    carts = await get_carts_by_user_id(user_id)
    total_sum = sum([cart.quantity * (await get_product_by_id(cart.product_id)).price for cart in carts])
    return total_sum


async def add_order(user_id, status, price, client_name, address, phone_number, pay):
    async with async_session() as session:
        order = Order(
            user_id=user_id,
            status=status,
            price=price,
            client_name=client_name,
            address=address,
            phone_number=phone_number,
            pay=pay
        )
        session.add(order)
        await session.flush()
        order_id = order.id
        carts = await get_carts_by_user_id(user_id)
        for cart in carts:
            cart_id = cart.id
            ordercart = OrderCart(
                cart_id = cart_id,
                order_id = order_id
            )
            session.add(ordercart)
            cart.status = "ordered"
            session.add(cart)
        await session.commit()


async def add_order_cart(cart_id, order_id):
    async with async_session() as session:
        order_cart = OrderCart(cart_id=cart_id, order_id=order_id)
        session.add(order_cart)
        session.commit()


async def add_question(user_id, question, status, phone_number = None):
    async with async_session() as session:
        appeal = Appeal(user_id=user_id, question=question, status=status, phone_number=phone_number)
        session.add(appeal)
        await session.commit()


async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user is None:
            user = User(tg_id=tg_id)
            session.add(user)
        await session.commit()


async def get_all_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
    return users


async def get_all_question():
    async with async_session() as session:
        q = await session.scalars(select(Appeal).where(Appeal.status == "new"))
    return q


async def get_appeal_by_id(appeal_id):
    async with async_session() as session:
        appeal = await session.scalar(select(Appeal).where(Appeal.id == appeal_id))
    return appeal


async def update_appeal_status(appeal_id):
    async with async_session() as session:
        appeal = await session.scalar(select(Appeal).where(Appeal.id == appeal_id))
        appeal.status = "answered"
        await session.commit()


async def get_orders_by_user_id(user_id):
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.user_id == user_id))
    return orders


async def get_order_by_id(order_id):
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()


async def get_order_items(order_id):
    async with async_session() as session:
        order_carts = await session.execute(
            select(OrderCart.cart_id).where(OrderCart.order_id == order_id)
        )
        carts_ids = [cart[0] for cart in order_carts]
        if carts_ids:
            items = await session.execute(
                select(Cart.id,
                       Cart.product_id,
                       Cart.quantity,
                       Product.name,
                       Product.price,
                       Product.photo).join(Product, Cart.product_id == Product.id).where(Cart.id.in_(carts_ids))
            )
        return items.all()


# АДМИН-ФУНКЦИИ ДЛЯ УПРАВЛЕНИЯ ТОВАРАМИ

async def add_product(name: str, info: str, photo: str, price: int, type_id: int):
    """Добавление нового товара"""
    async with async_session() as session:
        product = Product(
            name=name,
            info=info,
            photo=photo,
            price=price,
            type_id=type_id
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product


async def delete_product(product_id: int):
    """Удаление товара по ID"""
    async with async_session() as session:
        # Сначала проверяем, есть ли товар в корзинах
        carts = await session.scalars(select(Cart).where(Cart.product_id == product_id))
        if carts:
            # Удаляем связанные записи из корзин
            for cart in carts:
                await session.delete(cart)

        # Удаляем товар
        result = await session.execute(delete(Product).where(Product.id == product_id))
        await session.commit()
        return result.rowcount > 0


async def update_product(product_id: int, **kwargs):
    """Обновление данных товара"""
    async with async_session() as session:
        result = await session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**kwargs)
        )
        await session.commit()
        return result.rowcount > 0


async def get_all_products():
    """Получение всех товаров"""
    async with async_session() as session:
        products = await session.scalars(
            select(Product)
        )
        return products.all()


async def get_products_by_type(type_id: int):
    """Получение товаров по категории"""
    async with async_session() as session:
        products = await session.scalars(
            select(Product)
            .where(Product.type_id == type_id)
        )
        return products.all()


async def get_product_with_type(product_id: int):
    """Получение товара с информацией о категории"""
    async with async_session() as session:
        product = await session.scalar(
            select(Product)
            .where(Product.id == product_id)
        )
        return product


async def get_product_details(product_id: int):
    """Получение полной информации о товаре"""
    async with async_session() as session:
        product = await session.scalar(
            select(Product)
            .where(Product.id == product_id)
        )
        return product