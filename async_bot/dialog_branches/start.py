from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from async_bot.dialog_branches.clients.states import FSMGreeting
from database.crud import update_user
from database.models import User


async def command_start(message: types.Message, session: AsyncSession, user: User, state: FSMContext):
    await message.answer(
        "Привет, я бот <b>Охоткин</b> — Ваш личный помощник в планировании отдыха.",
        reply_markup=ReplyKeyboardRemove())
    await state.finish()
    
    if user is None:
        user = User(chat_id=message.chat.id, username=message.chat.username, name=message.chat.first_name)
        await update_user(user, session)

        await FSMGreeting.name.set()
        await message.answer("Подскажите, как к Вам лучше обращаться?")


def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=["start"], state="*", chat_type=types.ChatType.PRIVATE)
