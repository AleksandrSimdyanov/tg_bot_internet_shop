# from aiogram import F, Router
# from aiogram.types import Message
# import keyboards as kb
# import app.database.requests as rq
#
# admin_router = Router()
#
# @admin_router.message((F.text == "/admin") & (F.from_user.id == 835168779))
# async def admin_cmd(message: Message):
#     await message.answer("Выберите дейтсвие", reply_markup=kb.admin_kb)
#     return
#
#
# @admin_router.message(F.text == "Посмотреть вопросы")
# async def help_cmd(message: Message):
#     appeals = await rq.get_all_question()
#     await message.answer(f"Вот список вопросов от пользователей:\n")
#     for i, appeal in enumerate(appeals, start = 1):
#         await message.answer(f"{i}. {appeal.question}(id пользователя:{appeal.user_id},"
#                  f"телефон: {appeal.phone_number})\n", reply_markup= await kb.appeal_kb(appeal.id))