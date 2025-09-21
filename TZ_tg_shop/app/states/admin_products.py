from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import app.database.requests as rq
import keyboards as kb

admin_products_router = Router()


class AddProduct(StatesGroup):
    type = State()
    name = State()
    info = State()
    price = State()
    photo = State()


class EditProduct(StatesGroup):
    field = State()
    value = State()


# Главное меню админа
@admin_products_router.message(Command("admin"))
async def admin_menu(message: Message):
    if message.from_user.id == 835168779:  # Ваш ID
        await message.answer("👨‍💻 Панель администратора", reply_markup=kb.admin_kb)
    else:
        await message.answer("❌ Доступ запрещен")


# Добавление товара
@admin_products_router.message(F.text == "Добавить товар")
async def add_product_start(message: Message, state: FSMContext):
    await message.answer("Выберите категорию:", reply_markup=await kb.admin_types_kb("add"))
    await state.set_state(AddProduct.type)


@admin_products_router.callback_query(AddProduct.type, F.data.startswith("admin_add_type_"))
async def add_product_type(call: CallbackQuery, state: FSMContext):
    type_id = int(call.data.split("_")[3])
    type_obj = await rq.get_type_by_id(type_id)
    await state.update_data(type_id=type_id, type_name=type_obj.ru_name)
    await call.message.answer(f"Категория: {type_obj.ru_name}\nВведите название товара:",
                              reply_markup=kb.admin_cancel_kb)
    await state.set_state(AddProduct.name)
    await call.answer()


@admin_products_router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание товара:", reply_markup=kb.admin_cancel_kb)
    await state.set_state(AddProduct.info)


@admin_products_router.message(AddProduct.info)
async def add_product_info(message: Message, state: FSMContext):
    await state.update_data(info=message.text)
    await message.answer("Введите цену товара:", reply_markup=kb.admin_cancel_kb)
    await state.set_state(AddProduct.price)


@admin_products_router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await message.answer("Отправьте фото товара или введите file_id:", reply_markup=kb.admin_cancel_kb)
        await state.set_state(AddProduct.photo)
    except ValueError:
        await message.answer("❌ Введите корректную цену (число):")


@admin_products_router.message(AddProduct.photo, F.photo)
async def add_product_photo_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    data = await state.get_data()

    await rq.add_product(
        name=data['name'],
        info=data['info'],
        photo=file_id,
        price=data['price'],
        type_id=data['type_id']
    )

    await message.answer("✅ Товар успешно добавлен!", reply_markup=kb.admin_after_add_kb)
    await state.clear()


@admin_products_router.message(AddProduct.photo)
async def add_product_photo_text(message: Message, state: FSMContext):
    photo = message.text
    data = await state.get_data()

    await rq.add_product(
        name=data['name'],
        info=data['info'],
        photo=photo,
        price=data['price'],
        type_id=data['type_id']
    )

    await message.answer("✅ Товар успешно добавлен!", reply_markup=kb.admin_after_add_kb)
    await state.clear()


# Удаление товара
@admin_products_router.message(F.text == "Удалить товар")
async def delete_product_start(message: Message):
    await message.answer("Выберите категорию:", reply_markup=await kb.admin_types_kb("delete"))


@admin_products_router.callback_query(F.data.startswith("admin_delete_type_"))
async def delete_product_category(call: CallbackQuery):
    type_id = int(call.data.split("_")[3])
    products = await rq.get_products(type_id)

    if not products:
        await call.message.answer("❌ В этой категории нет товаров")
        return

    await call.message.answer("Выберите товар для удаления:",
                              reply_markup=await kb.admin_products_kb(type_id, "delete"))
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_delete_product_"))
async def delete_product_confirm(call: CallbackQuery):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_by_id(product_id)

    await call.message.answer(
        f"❓ Удалить товар?\n\n"
        f"📦 {product.name}\n"
        f"💰 {product.price} руб.\n\n"
        f"Это действие нельзя отменить!",
        reply_markup=await kb.admin_confirm_delete_kb(product_id)
    )
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_confirm_delete_"))
async def delete_product_final(call: CallbackQuery):
    product_id = int(call.data.split("_")[3])
    success = await rq.delete_product(product_id)

    if success:
        await call.message.answer("✅ Товар удален!")
    else:
        await call.message.answer("❌ Ошибка при удалении товара")
    await call.answer()


@admin_products_router.callback_query(F.data == "admin_cancel_delete")
async def cancel_delete(call: CallbackQuery):
    await call.message.answer("❌ Удаление отменено")
    await call.answer()


# Обработка кнопок отмены и возврата
@admin_products_router.callback_query(F.data == "admin_cancel")
async def admin_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("❌ Действие отменено", reply_markup=kb.admin_kb)
    await call.answer()


@admin_products_router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery):
    await call.message.answer("👨‍💻 Панель администратора", reply_markup=kb.admin_kb)
    await call.answer()


@admin_products_router.callback_query(F.data == "admin_back_types")
async def admin_back_types(call: CallbackQuery):
    await call.message.answer("Выберите категорию:", reply_markup=await kb.admin_types_kb("delete"))
    await call.answer()


@admin_products_router.callback_query(F.data == "admin_add_more")
async def admin_add_more(call: CallbackQuery):
    await call.message.answer("Выберите категорию:", reply_markup=await kb.admin_types_kb("add"))
    await call.answer()


@admin_products_router.callback_query(F.data == "admin_back_menu")
async def admin_back_menu(call: CallbackQuery):
    await call.message.answer("👨‍💻 Панель администратора", reply_markup=kb.admin_kb)
    await call.answer()


# РЕДАКТИРОВАНИЕ ТОВАРА
@admin_products_router.message(F.text == "✏️ Редактировать товар")
async def edit_product_start(message: Message):
    await message.answer("Выберите категорию:", reply_markup=await kb.admin_types_kb("edit"))


@admin_products_router.callback_query(F.data.startswith("admin_edit_type_"))
async def edit_product_category(call: CallbackQuery):
    type_id = int(call.data.split("_")[3])
    products = await rq.get_products(type_id)

    if not products:
        await call.message.answer("❌ В этой категории нет товаров")
        return

    await call.message.answer("Выберите товар для редактирования:",
                              reply_markup=await kb.admin_products_kb(type_id, "edit"))
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_product_"))
async def edit_product_select(call: CallbackQuery):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_details(product_id)

    if not product:
        await call.message.answer("❌ Товар не найден")
        return

    message_text = (
        f"📦 Товар: {product.name}\n"
        f"📝 Описание: {product.info}\n"
        f"💰 Цена: {product.price} руб.\n"
        f"🖼️ Фото: {'📷 Прикреплено' if product.photo else '❌ Отсутствует'}\n\n"
        f"Выберите что хотите изменить:"
    )

    await call.message.answer(message_text, reply_markup=await kb.admin_edit_product_kb(product_id))
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_name_"))
async def edit_product_name_start(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_by_id(product_id)

    await state.update_data(product_id=product_id, current_field="name")
    await call.message.answer(f"Текущее название: {product.name}\nВведите новое название:",
                              reply_markup=kb.admin_cancel_kb)
    await state.set_state(EditProduct.value)
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_info_"))
async def edit_product_info_start(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_by_id(product_id)

    await state.update_data(product_id=product_id, current_field="info")
    await call.message.answer(f"Текущее описание: {product.info}\nВведите новое описание:",
                              reply_markup=kb.admin_cancel_kb)
    await state.set_state(EditProduct.value)
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_price_"))
async def edit_product_price_start(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_by_id(product_id)

    await state.update_data(product_id=product_id, current_field="price")
    await call.message.answer(f"Текущая цена: {product.price} руб.\nВведите новую цену:",
                              reply_markup=kb.admin_cancel_kb)
    await state.set_state(EditProduct.value)
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_photo_"))
async def edit_product_photo_start(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[3])

    await state.update_data(product_id=product_id, current_field="photo")
    await call.message.answer("Отправьте новое фото или введите file_id:", reply_markup=kb.admin_cancel_kb)
    await state.set_state(EditProduct.value)
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_type_"))
async def edit_product_type_start(call: CallbackQuery):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_details(product_id)

    await call.message.answer(
        f"Текущая категория: {product.type.ru_name}\nВыберите новую категорию:",
        reply_markup=await kb.admin_edit_types_kb(product_id)
    )
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_change_type_"))
async def edit_product_type_change(call: CallbackQuery):
    data_parts = call.data.split("_")
    product_id = int(data_parts[3])
    new_type_id = int(data_parts[4])

    success = await rq.update_product(product_id, type_id=new_type_id)

    if success:
        product = await rq.get_product_details(product_id)
        new_type = await rq.get_type_by_id(new_type_id)
        await call.message.answer(f"✅ Категория изменена на: {new_type.ru_name}")
    else:
        await call.message.answer("❌ Ошибка при изменении категории")
    await call.answer()


@admin_products_router.message(EditProduct.value, F.photo)
async def edit_product_photo_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    field = data['current_field']

    file_id = message.photo[-1].file_id
    success = await rq.update_product(product_id, photo=file_id)

    if success:
        await message.answer("✅ Фото обновлено!", reply_markup=kb.admin_after_action_kb)
    else:
        await message.answer("❌ Ошибка при обновлении фото")

    await state.clear()


@admin_products_router.message(EditProduct.value)
async def edit_product_value(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    field = data['current_field']
    value = message.text

    # Валидация для цены
    if field == "price":
        try:
            value = int(value)
        except ValueError:
            await message.answer("❌ Цена должна быть числом. Попробуйте еще раз:")
            return

    update_data = {field: value}
    success = await rq.update_product(product_id, **update_data)

    if success:
        field_names = {
            "name": "название",
            "info": "описание",
            "price": "цена",
            "photo": "фото"
        }
        await message.answer(f"✅ {field_names[field].capitalize()} обновлено!", reply_markup=kb.admin_after_action_kb)
    else:
        await message.answer("❌ Ошибка при обновлении")

    await state.clear()


@admin_products_router.callback_query(F.data.startswith("admin_edit_done_"))
async def edit_product_done(call: CallbackQuery):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_details(product_id)

    message_text = (
        f"✅ Товар обновлен!\n\n"
        f"📦 {product.name}\n"
        f"📝 {product.info}\n"
        f"💰 {product.price} руб.\n"
        f"🖼️ {'📷 Фото прикреплено' if product.photo else '❌ Фото отсутствует'}"
    )

    await call.message.answer(message_text, reply_markup=kb.admin_after_action_kb)
    await call.answer()


@admin_products_router.callback_query(F.data.startswith("admin_edit_back_"))
async def edit_product_back(call: CallbackQuery):
    product_id = int(call.data.split("_")[3])
    product = await rq.get_product_details(product_id)

    message_text = (
        f"📦 Товар: {product.name}\n"
        f"📝 Описание: {product.info}\n"
        f"💰 Цена: {product.price} руб.\n"
        f"📂 Категория: {product.type.ru_name}\n\n"
        f"Выберите что хотите изменить:"
    )

    await call.message.answer(message_text, reply_markup=await kb.admin_edit_product_kb(product_id))
    await call.answer()


@admin_products_router.callback_query(F.data == "admin_edit_more")
async def admin_edit_more(call: CallbackQuery):
    await call.message.answer("Выберите категорию:", reply_markup=await kb.admin_types_kb("edit"))
    await call.answer()