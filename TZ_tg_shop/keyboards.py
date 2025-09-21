from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           ReplyKeyboardMarkup,
                           KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app.database.requests as rq

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог 🗂"), KeyboardButton(text="Корзина 🛍")],
        [KeyboardButton(text="Заказы 📦"), KeyboardButton(text="Помощь 🆘")]
    ], resize_keyboard=True
)


async def types_kb(back=True):
    builder = InlineKeyboardBuilder()
    try:
        types = await rq.get_types()
        for type in types:
            button = InlineKeyboardButton(text=type.ru_name, callback_data=f"type_{type.id}")
            builder.row(button)
    except Exception as e:
        # Логируем ошибку, но возвращаем пустую клавиатуру с кнопкой назад
        print(f"Error getting types: {e}")

    if back:
        builder.row(InlineKeyboardButton(text="⏪Вернуться", callback_data="back_menu"))
    return builder.as_markup()


async def products_kb(type_id, back=True):
    builder = InlineKeyboardBuilder()
    try:
        products = await rq.get_products(type_id)
        for product in products:
            button = InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}")
            builder.row(button)
    except Exception as e:
        print(f"Error getting products: {e}")

    if back:
        builder.row(InlineKeyboardButton(text="⏪Вернуться", callback_data="back_section"))
    return builder.as_markup()


async def buy_kb(product_id):
    try:
        product = await rq.get_product_by_id(product_id)
        if product:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"Купить-1шт-{product.price} рублей", callback_data=f"indicate_{product.id}")]
                ]
            )
            return kb
        else:
            # Если товар не найден, возвращаем пустую клавиатуру
            return InlineKeyboardMarkup(inline_keyboard=[])
    except Exception as e:
        print(f"Error creating buy keyboard: {e}")
        # Возвращаем пустую клавиатуру в случае ошибки
        return InlineKeyboardMarkup(inline_keyboard=[])


async def size_kb(product_id):
    builder = InlineKeyboardBuilder()
    product = await rq.get_product_by_id(product_id)
    sizes = product.size.split(", ")
    for size in sizes:
        button = InlineKeyboardButton(text=size, callback_data=f"buy_{product.id}_{size}")
        builder.add(button)
    builder.row(InlineKeyboardButton(text="⏪Вернуться", callback_data="back_section"))
    return builder.as_markup()

async def new_buy_kb(product_id, us_id, quantity):
    product = await rq.get_product_by_id(product_id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Купить-{product.price} рублей", callback_data=f"buy_{product.id}")],
            [InlineKeyboardButton(text="➖", callback_data=f"minus_{product_id}"), InlineKeyboardButton(text=f"{quantity} шт.", callback_data="count"), InlineKeyboardButton(text="➕", callback_data=f"plus_{product_id}")],
            [InlineKeyboardButton(text=f"Корзина ({await rq.get_sum_cart_by_user_id(us_id)} рублей)", callback_data=f"cart_{us_id}")],
        ]
    )
    return kb

make_order_kb =  InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сделать заказ", callback_data=f"order")]
        ]
    )
pay_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="СБП")],
        [KeyboardButton(text="Банковская карта")],
        [KeyboardButton(text="Наличные")]
    ], resize_keyboard=True
)

phone_number_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Контакт", request_contact=True)]
    ], resize_keyboard=True
)

yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ], resize_keyboard=True
)

async def order_kb(orders):
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.add(InlineKeyboardButton(text=f"Заказ № {order.id} - {order.status}", callback_data=f"order_{order.id}"))
        builder.adjust(1)
    return builder.as_markup()

async def appeal_kb(appeal_id):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data=f"appeal_{appeal_id}")]
        ]
    )
    return kb


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Посмотреть вопросы")],
        [KeyboardButton(text="➕ Добавить товар"), KeyboardButton(text="🗑️ Удалить товар")],
        [KeyboardButton(text="✏️ Редактировать товар")]
    ],
    resize_keyboard=True
)


async def admin_types_kb(action: str = "view"):
    """
    Клавиатура категорий для админа
    action: "add", "delete", "edit", "view"
    """
    builder = InlineKeyboardBuilder()
    types = await rq.get_types()

    for type in types:
        callback_data = f"admin_{action}_type_{type.id}"
        button = InlineKeyboardButton(text=type.ru_name, callback_data=callback_data)
        builder.row(button)

    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="admin_back"))
    return builder.as_markup()


async def admin_products_kb(type_id: int, action: str = "view"):
    """
    Клавиатура товаров для админа
    action: "delete", "edit"
    """
    builder = InlineKeyboardBuilder()
    products = await rq.get_products(type_id)

    for product in products:
        callback_data = f"admin_{action}_product_{product.id}"
        button = InlineKeyboardButton(text=product.name, callback_data=callback_data)
        builder.row(button)

    builder.row(InlineKeyboardButton(text="⏪ Назад к категориям", callback_data="admin_back_types"))
    return builder.as_markup()


async def admin_edit_product_kb(product_id: int):
    """Клавиатура для редактирования товара"""
    builder = InlineKeyboardBuilder()

    buttons = [
        ("✏️ Название", f"admin_edit_name_{product_id}"),
        ("📝 Описание", f"admin_edit_info_{product_id}"),
        ("💰 Цена", f"admin_edit_price_{product_id}"),
        ("🖼️ Фото", f"admin_edit_photo_{product_id}"),
        ("📂 Категория", f"admin_edit_type_{product_id}"),
        ("✅ Готово", f"admin_edit_done_{product_id}")
    ]

    for text, callback_data in buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))

    builder.adjust(2)
    return builder.as_markup()


async def admin_edit_field_kb(product_id: int, field: str):
    """Клавиатура для конкретного поля редактирования"""
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="✏️ Изменить", callback_data=f"admin_edit_{field}_{product_id}"),
        InlineKeyboardButton(text="⏪ Назад", callback_data=f"admin_edit_back_{product_id}")
    )

    return builder.as_markup()


async def admin_confirm_delete_kb(product_id: int):
    """Клавиатура подтверждения удаления"""
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="✅ Да", callback_data=f"admin_confirm_delete_{product_id}"),
        InlineKeyboardButton(text="❌ Нет", callback_data="admin_cancel_delete")
    )

    return builder.as_markup()


# Клавиатура для выбора действия после добавления/редактирования товара
admin_after_action_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать еще", callback_data="admin_edit_more")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="admin_back_menu")]
    ]
)

# Клавиатура для отмены действий
admin_cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_cancel")]
    ]
)


async def admin_edit_types_kb(product_id: int):
    """Клавиатура выбора категории для редактирования"""
    builder = InlineKeyboardBuilder()
    types = await rq.get_types()

    for type in types:
        callback_data = f"admin_change_type_{product_id}_{type.id}"
        button = InlineKeyboardButton(text=type.ru_name, callback_data=callback_data)
        builder.row(button)

    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"admin_edit_back_{product_id}"))
    return builder.as_markup()