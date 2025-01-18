import asyncio
import logging
import os
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv, find_dotenv
from user_private import user_private_router
load_dotenv(find_dotenv())

"""ExtendedBot  наследуется от Aiogram Bot, с добавлением атрибутов file_system, admins_list, price"""
bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))

dp = Dispatcher()
dp.include_routers(user_private_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit by keyboard')
