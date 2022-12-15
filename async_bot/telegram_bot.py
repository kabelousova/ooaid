import logging
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv

from async_bot.dialog_branches import register_branches
from async_bot.middleware import DbSessionMiddleware

load_dotenv()

token = "5218081857:AAFLWlJdwXmg6D_SjYiQBSmNsKs94CQE9E4"


async def default(message: types.Message):
    await message.answer("К сожалению, я еще не умею отвечать на такое")


class AsyncBot:

    def __init__(self, sessionmaker):
        self.bot = Bot(token, parse_mode=types.ParseMode.HTML)
        self._dp: Dispatcher = Dispatcher(self.bot, storage=MemoryStorage())
        self._dp.middleware.setup(DbSessionMiddleware(sessionmaker))

        logging.basicConfig(
            filename="log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )

    async def start(self):
        register_branches(self._dp)
        self._dp.register_message_handler(default, state='*', content_types=types.ContentType.ANY)

        await self._set_commands()

        try:
            await self._dp.start_polling()
        finally:
            await self._dp.storage.close()
            await self._dp.storage.wait_closed()
            await self.bot.session.close()

    async def _set_commands(self):
        commands = [
            BotCommand(command="help", description="Что я умею"),
            BotCommand(command="order", description="Планирование вашего отдыха"),
            BotCommand(command="news", description="Новости"),
            # BotCommand(command="discounts", description="Скидки"),
            BotCommand(command="sales", description="Акции"),
        ]

        await self.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
