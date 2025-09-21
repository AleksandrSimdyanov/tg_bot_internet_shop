from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
import keyboards as kb
import app.database.requests as rq

user_router = Router()


@user_router.message(Command("start"))
async def start_cmd(message: Message):
    await rq.add_user(message.from_user.id)
    await message.answer("Добро пожаловать в наш бот."
                         "Нажмите на кнопку которая вас интересует!", reply_markup=kb.start_kb)

@user_router.message(F.text == "Каталог 🗂")
async def send_catalog(message: Message):
    await message.answer("Выберите раздел, чтобы вывести список товаров:"
                         , reply_markup=await kb.types_kb(back=True))


@user_router.callback_query(F.data.startswith("type_"))
async def show_types(call: CallbackQuery):
    type_id = call.data.split("_")[1]
    await call.message.edit_text("Выберете товар:", reply_markup=await kb.products_kb(type_id))
    await call.answer()


@user_router.callback_query(F.data.startswith("product_"))
async def show_product(call: CallbackQuery):
    product_id = call.data.split("_")[1]
    product = await rq.get_product_by_id(product_id)

    if not product:
        await call.answer("❌ Товар не найден")
        return

    type = await rq.get_type_by_id(product.type_id)
    if product.photo.endswith(".jpg"):
        photo = FSInputFile(f"app/database/images/{type.type}/{product.photo}")
    else:
        photo = product.photo
    information = (f"{product.name}\n"
                   f"Информация: {product.info}")
    await call.message.answer_photo(photo, caption=information, reply_markup=await kb.buy_kb(product.id))
    await call.answer()


@user_router.callback_query(F.data.startswith("indicate_"))
async def indicate_product(call: CallbackQuery):
    product_id = call.data.split("_")[1]
    user_id = call.from_user.id
    count = await rq.add_cart(user_id, product_id)
    await call.answer("Корзина обновлена")
    await call.message.edit_reply_markup(reply_markup=await kb.new_buy_kb(product_id, user_id, count))


@user_router.callback_query(F.data.startswith("plus_"))
async def make_plus(call: CallbackQuery):
    _, product_id = call.data.split("_")
    user_id = call.from_user.id
    count = await rq.add_cart(user_id, product_id)
    await call.message.edit_reply_markup(reply_markup=await kb.new_buy_kb(product_id, user_id, count))

@user_router.callback_query(F.data.startswith("minus_"))
async def make_minus(call: CallbackQuery):
    _, product_id = call.data.split("_")
    user_id = call.from_user.id
    count = await rq.remove_cart(user_id, product_id)
    if count > 0:
        await call.message.edit_reply_markup(reply_markup=await kb.new_buy_kb(product_id, user_id, count))
    elif count == 0:
        await call.message.edit_reply_markup(reply_markup=await kb.buy_kb(product_id))


@user_router.callback_query(F.data.startswith("back"))
async def get_back(call: CallbackQuery):
    data = call.data.split("_")[1]
    if data == "section":
        await call.message.answer("Выберите раздел, чтобы вывести список товаров:",
                                     reply_markup=await kb.types_kb(back=True))
        await call.answer()

    elif data == "menu":
        await call.message.answer("Добро пожаловать в наш бот. Здесь вы сможете выбрать аммуницию\n"
                         "для вашего любимого вида спорта\n"
                         "Нажмите на кнопку которая вас интересует!", reply_markup=kb.start_kb)
        await call.answer()


@user_router.message(F.text == "Корзина 🛍")
async def send_cart(message: Message):
    user_id = message.from_user.id
    carts = await rq.get_carts_by_user_id(user_id)
    answers = ""
    for i, cart in enumerate(carts, start=1):
        product = await rq.get_product_by_id(cart.product_id)
        answer = f"{i}. {product.name} в количестве {cart.quantity} шт.\n"
        answers += answer
    if len(answers) > 0:
        await message.answer(f"Вот ваша корзина\n"
                             f"{answers}", reply_markup= kb.make_order_kb)
    else:
        await message.answer("Ваша корзина пуста")


@user_router.message(F.text == "Заказы 📦")
async def send_order(message: Message):
    user_id = message.from_user.id
    orders = await rq.get_orders_by_user_id(user_id)
    if not orders:
        await message.answer("У вас пока нет заказов")
        return
    await message.answer("Вот ваши заказы:", reply_markup=await kb.order_kb(orders))


@user_router.callback_query(F.data.startswith("order_"))
async def show_order(call: CallbackQuery):
    order_id = call.data.split("_")[1]
    order = await rq.get_order_by_id(order_id)
    if not order:
        await call.message.answer("Заказ не найден")
        await call.answer()
        return
    order_items = await rq.get_order_items(order_id)
    message_text = (f"📦Заказ № {order.id}\n"
                    f"🕒Дата: {order.crated_at}\n"
                    f"👤Клиент: {order.client_name}\n"
                    f"📞Телефон: {order.phone_number}\n"
                    f"🏠 Адрес: {order.address}\n"
                    f"💳Оплата: {order.pay}\n"
                    f"🔄Статус: {order.status}\n"
                    f"💰Сумма: {order.price}\n"
                    f"🛒Состав заказа:\n")
    for item in order_items:
        message_text += f"{item.name} - {item.quantity} шт. * {item.price} руб.\n"
    await call.message.answer(message_text)
    await call.answer()