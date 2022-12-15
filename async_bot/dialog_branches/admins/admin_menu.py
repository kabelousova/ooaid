from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from async_bot.dialog_branches.admins.states import FSMAdminMenu

from database.models import User


async def open_admin_menu(message: types.Message, user: User):
    if user.role == "Admin":
        await message.answer("Добро пожаловать в меню администратора, вам доступны следующие команды:\n"
                             "  /add - добавить нового сотрудника\n"
                             "  /delete - убрать сотрудника\n"
                             "  /show - показать всех сотрудников\n"
                             "  /statistic - показать статистику по заявкам\n"
                             "Чтобы выйти из меню, просто напишите: \"Выйти\"",
                             reply_markup=ReplyKeyboardRemove())
        await FSMAdminMenu.menu.set()


async def exit_menu(message: types.Message, state: FSMContext):
    await message.answer("Вы вышли из меню администратора")
    await state.finish()


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(open_admin_menu, commands=["admin"], state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(exit_menu, Text("Выйти"), state=FSMAdminMenu.menu)
