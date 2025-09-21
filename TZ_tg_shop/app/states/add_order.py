from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
from app.database.requests import add_order
from keyboards import phone_number_kb, pay_kb, start_kb

add_order_router = Router()

class AddOrder(StatesGroup):
    client_name = State()
    address = State()
    phone_number = State()
    pay = State()

@add_order_router.callback_query(F.data == "order")
async def show_add_order(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Приступаем к оформлению заказа."
                                 "Отправьте ваше ФИО")
    await state.set_state(AddOrder.client_name)
    await call.answer()

@add_order_router.message(AddOrder.client_name)
async def add_order_name(message: Message, state: FSMContext):
    client_name = message.text
    await state.update_data(client_name=client_name)
    await state.set_state(AddOrder.address)
    await message.answer("Введите полный адрес")

@add_order_router.message(AddOrder.address)
async def add_order_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await state.set_state(AddOrder.phone_number)
    await message.answer("Введите номер телефона", reply_markup=phone_number_kb)

@add_order_router.message(AddOrder.phone_number)
async def add_order_phone_number(message: Message, state: FSMContext):
    contact = message.contact
    if contact:
        await state.update_data(phone_number=contact.phone_number)
    else:
        await state.update_data(phone_number=message.text)
    await state.set_state(AddOrder.pay)
    await message.answer("Введите способ оплаты", reply_markup=pay_kb)

@add_order_router.message(AddOrder.pay)
async def add_order_pay(message: Message, state: FSMContext):
    pay = message.text
    await state.update_data(pay=pay)
    data = await state.get_data()
    await add_order(
        user_id=message.from_user.id,
        client_name=data["client_name"],
        address=data["address"],
        phone_number=data["phone_number"],
        pay=pay,
        status="new",
        price=await rq.get_sum_cart_by_user_id(message.from_user.id),
    )
    await state.clear()
    await message.answer("Заказ оформлен", reply_markup=start_kb)