from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.database.requests as rq

response_router = Router()

class Response(StatesGroup):
    answer = State()

@response_router.callback_query(F.data.startswith("appeal_"))
async def get_appeal(call: CallbackQuery, state: FSMContext):
    appeal_id = call.data.split("_")[1]
    await state.update_data(appeal_id=appeal_id)
    await state.set_state(Response.answer)
    await call.message.answer("Введите ответ на вопрос")
    await call.answer()

@response_router.message(Response.answer)
async def get_answer(message: Message, state: FSMContext, bot: Bot):
    answer = message.text
    data = await state.get_data()
    appeal = await rq.get_appeal_by_id(data["appeal_id"])
    await bot.send_message(appeal.user_id,
                           f"Пришло сообщение от администратора:\n{answer}")
    await rq.update_appeal_status(appeal.id)
    await message.answer("Ответ отправлен!")
    await state.clear()