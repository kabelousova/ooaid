from aiogram import types, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from async_bot.dialog_branches.admins.states import FSMAdminMenu
from database.models import User


async def show_workers(message: types.Message, session: AsyncSession):
    query = select(User).filter(User.role == 'Worker')

    workers = (await session.execute(query)).scalars()

    for worker in workers:
        await message.answer(f'Работник: {worker.name}\n'
                             f' Telegram: @{worker.username}\n'
                             f' Chat_id: {worker.chat_id}')


def register_show_workers_handlers(dp: Dispatcher):
    dp.register_message_handler(show_workers, commands=['show'], state=FSMAdminMenu.menu)
