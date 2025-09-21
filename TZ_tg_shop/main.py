import os
from aiogram import Bot, Dispatcher
import asyncio
from app.database.models import async_main
from dotenv import load_dotenv
from app.handlers.user_handler import user_router
from app.states.do_appeal import do_appeal_router
from app.states.add_order import add_order_router
from app.states.admin_products import admin_products_router


load_dotenv()

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher()


async def main():
    await async_main()
    dp.include_routers(user_router,
                       admin_products_router,
                       # admin_router,
                       do_appeal_router,
                       add_order_router,
                       )
    await dp.start_polling(bot)
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")