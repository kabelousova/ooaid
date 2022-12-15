from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from async_bot.dialog_branches.admins.states import FSMAdminMenu
from async_bot.dialog_branches.utils import create_keyboard_reply
from async_bot.filters.NotCommandFilter import NotCommandFilter
from database.crud import get_user_by_username, update_user, get_user_by_id

back_button = create_keyboard_reply(["Назад"])


async def delete_worker_menu(message: types.Message):
    await message.answer("Введите никнейм пользователя или chat_id, чтобы удалить его из списка сотрудников.\n"
                         "Сотрудник перестанет получать уведомления о новых заявках.",
                         reply_markup=back_button)
    await FSMAdminMenu.delete.set()


async def delete_worker(message: types.Message, session: AsyncSession):
    try:
        user_del = await get_user_by_id(int(message.text), session)
    except:
        user_del = await get_user_by_username(message.text, session)

    if user_del is None:
        await message.answer("Такого пользователя нет, либо он еще не писал боту", reply_markup=back_button)
    elif user_del.role == "Client":
        await message.answer("Пользователь не является сотрудником", reply_markup=back_button)
    elif user_del.role == "Admin":
        await message.answer("Пользователь является администратором", reply_markup=back_button)
    else:
        user_del.role = "Client"
        await update_user(user_del, session)

        await message.answer("Сотрудник успешно понижен", reply_markup=ReplyKeyboardRemove())
        await message.bot.send_message(user_del.chat_id, "Администратор понизил вас, теперь вам перестанут "
                                                         "приходить заявки от клиентов")
        await FSMAdminMenu.menu.set()


async def back_message(message: types.Message):
    await message.answer("Хорошо", reply_markup=ReplyKeyboardRemove())
    await FSMAdminMenu.menu.set()


def register_delete_worker_handlers(dp: Dispatcher):
    dp.register_message_handler(delete_worker_menu, commands=["delete"], state=FSMAdminMenu.menu)
    dp.register_message_handler(back_message, Text("Назад"), state=FSMAdminMenu.delete)
    dp.register_message_handler(delete_worker, NotCommandFilter(), state=FSMAdminMenu.delete)
