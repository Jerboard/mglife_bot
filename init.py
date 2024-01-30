from aiogram import Dispatcher
from aiogram.types.bot_command import BotCommand
from aiogram import Bot
from aiogram.enums import ParseMode

from dotenv import load_dotenv
from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler


import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass


load_dotenv ()
loop = asyncio.get_event_loop()
dp = Dispatcher()
bot = Bot(getenv("TOKEN"), parse_mode=ParseMode.HTML)

DEBUG = bool(int(getenv('DEBUG')))

ENGINE = create_async_engine(url=getenv('DB_URL'))
account = getenv('ACCOUNT')
secret_key = getenv('SECRET_KEY')
group_id = getenv('GROUP_ID')

# ADMINS = [650850638, 524275902, 1456925942]
ADMINS = [650850638, 1456925942]
MY_ID = getenv('MY_ID')

scheduler = AsyncIOScheduler()


async def set_main_menu() -> None:
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Перезапустить бот'),
    ]

    sent = await bot.set_my_commands(main_menu_commands)
