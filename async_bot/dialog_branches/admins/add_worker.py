from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from async_bot.dialog_branches.admins.states import FSMAdminMenu
from async_bot.dialog_branches.utils import create_keyboard_reply
from async_bot.filters.NotCommandFilter import NotCommandFilter
from database.crud import get_user_by_username, update_user, get_user_by_id
from database.models import User

back_button = create_keyboard_reply(["Назад"])


async def add_worker_menu(message: types.Message):
    await message.answer("Введите никнейм пользователя или его chat_id, чтобы повысить его до сотрудника.\n"
                         "Сотрудники получают уведомления о новых заявках.",
                         reply_markup=back_button)
    await FSMAdminMenu.add.set()


async def add_worker(message: types.Message, session: AsyncSession):
    try:
        user_add = await get_user_by_id(int(message.text), session)
    except Exception as _:
        user_add = await get_user_by_username(message.text, session)

    if user_add is None:
        await message.answer("Такого пользователя нет, либо он еще не писал боту", reply_markup=back_button)
    elif user_add.role == "Worker":
        await message.answer("Пользователь уже является работником", reply_markup=back_button)
    elif user_add.role == "Admin":
        await message.answer("Пользователь является администратором", reply_markup=back_button)
    else:
        user_add.role = "Worker"
        await update_user(user_add, session)

        await message.answer("Пользователь успешно повышен до сотрудника", reply_markup=ReplyKeyboardRemove())
        await message.bot.send_message(user_add.chat_id, "Администратор сделал вас сотрудником, теперь вам будут "
                                                         "приходить новые заявки от клиентов")
        await FSMAdminMenu.menu.set()


async def back_message(message: types.Message, session: AsyncSession, user: User, state: FSMContext):
    await message.answer("Хорошо", reply_markup=ReplyKeyboardRemove())
    await FSMAdminMenu.menu.set()


def register_add_worker_handlers(dp: Dispatcher):
    dp.register_message_handler(add_worker_menu, commands=["add"], state=FSMAdminMenu.menu)
    dp.register_message_handler(back_message, Text("Назад"), state=FSMAdminMenu.add)
    dp.register_message_handler(add_worker, NotCommandFilter(), state=FSMAdminMenu.add)
