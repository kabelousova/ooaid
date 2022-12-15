from aiogram import types, Dispatcher, md
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from async_bot.dialog_branches.clients.questionnaire import make_order
from async_bot.dialog_branches.clients.states import FSMGreeting
from async_bot.dialog_branches.utils import get_number, create_keyboard_inline, Button, callback_data_leave_order
from async_bot.filters.NotCommandFilter import NotCommandFilter
from database.crud import *
from email_validator import validate_email, EmailNotValidError


async def greeting_name(message: types.Message, session: AsyncSession, user: User):
    user.name = message.text
    await update_user(user, session)

    await FSMGreeting.next()
    await message.answer(f"Отлично, {md.quote_html(user.name)}, рад с Вами познакомиться!")
    await message.answer("Оставьте, пожалуйста, номер для связи")


async def greeting_phone_number(message: types.Message, session: AsyncSession, user: User):
    phone_number = get_number(message.text)

    if phone_number is not None:
        user.phone_number = phone_number.national_number
        await update_user(user, session)

        await FSMGreeting.next()
        await message.answer("Я был бы очень рад, если Вы поделитесь своей почтой 😊\n"
                             "Но Вы можете отказаться, просто написав <b>Нет</b>.")
    else:
        await message.answer("Мне кажется, таких телефонов не бывает.\n\n"
                             "Давайте проверим 😊")


async def greeting_email(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    if '@' in message.text:
        try:
            email = validate_email(message.text).email

            user.email = email
            await update_user(user, session)
        except EmailNotValidError:
            await message.answer("Мне кажется, таких адресов не бывает.\n\n"
                                 "Давайте проверим 😊")
            return

    await state.finish()
    await message.answer("Хорошо! Мне не терпится перейти к планированию Вашего отдыха!")
    await message.answer("Вы уже готовы оставить заявку?", reply_markup=create_keyboard_inline(
        [Button("Да", callback_data_leave_order.new(answer="yes")),
         Button("Нет", callback_data_leave_order.new(answer="no"))]
    ))

    await make_order(message, state)


async def callback_leave_order_yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    await make_order(callback.message, state)


async def callback_leave_order_no(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    await callback.message.answer("Хорошо, определяйтесь! Я буду ждать Вашего решения! До встречи!")


def register_greeting(dp: Dispatcher):
    dp.register_message_handler(greeting_name, NotCommandFilter(), state=FSMGreeting.name)
    dp.register_message_handler(greeting_phone_number, NotCommandFilter(), state=FSMGreeting.phone_number)
    dp.register_message_handler(greeting_email, NotCommandFilter(), state=FSMGreeting.email)

    dp.register_callback_query_handler(callback_leave_order_yes, callback_data_leave_order.filter(answer="yes"))
    dp.register_callback_query_handler(callback_leave_order_no, callback_data_leave_order.filter(answer="no"))
