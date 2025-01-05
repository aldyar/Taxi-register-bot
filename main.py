import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.database.models import async_main
from app.user import user
from app.handlers.admin import admin
from app.handlers.admin_rassylka import admin1
from app.handlers.admin_verification import admin2

async def main():   
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(admin,admin1,admin2,user)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


async def on_startup(dispatcher):
    await async_main()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass