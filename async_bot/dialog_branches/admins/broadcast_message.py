from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from async_bot.dialog_branches.admins.states import FSMAdminMenu


async def broadcast_message_menu(message: types.Message):
    await message.answer('Включен режим отправки ОДНОГО, следующего вашего сообщений всем пользователям')

    await FSMAdminMenu.broadcast.set()


async def broadcast_message(message: types.Message, session: AsyncSession):
    await message.answer('Рассылка начата, вы возвращены в главное меню администратора!')

    await FSMAdminMenu.menu.set()
