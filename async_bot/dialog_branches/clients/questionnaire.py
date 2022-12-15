import datetime

from aiogram import types, Dispatcher, md
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, ContentType
from speech_recognition import UnknownValueError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from async_bot.dialog_branches.clients.states import FSMPoll, FSMVoice
from async_bot.dialog_branches.utils import create_keyboard_inline, callback_data_order, Button, \
    callback_data_make_order, create_keyboard_reply, convert_voice
from async_bot.filters.NegativeAnswer import NegativeAnswer
from async_bot.filters.NotCommandFilter import NotCommandFilter
from database.crud import update_order
from database.models import User, Order

yes_no_keyboard = create_keyboard_reply(["Да", "Нет"])


async def make_order(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer("Вы можете записать голосовое сообщение, подробно рассказав о ваших планах на отдых. "
                         "Или же можете пройти небольшой опрос.",
                         reply_markup=create_keyboard_inline(
                             [Button("Голосовое сообщение", callback_data_make_order.new(type="voice")),
                              Button("Опрос", callback_data_make_order.new(type="poll"))
                              ]
                         ))


async def voice_start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    await callback.message.answer("Расскажите мне, как бы вы хотели провести свой отдых.\n"
                                  "Возможно следующие вопросы помогут вам точнее описать свой отдых:\n\n"
                                  "  👉 Когда планируете отдых? 📅\n"
                                  "  👉 На сколько дней планируется отдых? 🏡\n"
                                  "  👉 Сколько вас человек? Взрослых, детей? 👨‍👩‍👧\n"
                                  "  👉 Уже выбрали отель? Если да, то какой?\n"
                                  "  👉 Нужен трансфер? Если да, то из какого города?🚌\n"
                                  "  👉 Есть ли у вас страховка?\n"
                                  "  👉 Любые ваши пожелания",
                                  reply_markup=ReplyKeyboardRemove())

    await FSMVoice.voice.set()


async def get_voice(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    voice = (await message.voice.get_file())

    try:
        about_order = await convert_voice(voice, message.bot)

        await message.answer(
            "Спасибо, уже работаю над Вашим отдыхом и в ближайшее время направлю лучшие варианты! До встречи!")
        await state.finish()

        order = Order(user_id=user.chat_id,
                      about_order=about_order,
                      create_date=datetime.datetime.utcnow())

        await update_order(order, session)

        order_text = (f"Пользователь @{md.quote_html(user.username)} оставил заявку:\n"
                      f"   Имя: {md.quote_html(user.name)}\n"
                      f"   Телефон: {md.quote_html(user.phone_number)}\n"
                      f"   Почта: {md.quote_html(user.email)}\n\n"
                      f"О заявке:\n" + about_order)

        query = select(User).filter(User.role == "Worker")

        workers = (await session.execute(query)).scalars()

        for worker in workers:
            await message.bot.send_message(worker.chat_id, order_text,
                                           reply_markup=create_keyboard_inline(
                                               [Button("Взять заявку",
                                                       callback_data_order.new(id=order.order_id, action="take"))]
                                           ))
            await message.forward(worker.chat_id)
    except UnknownValueError:
        await message.answer("Простите, я не смог разобрать ваше сообщение, попробуйте еще раз")


async def poll_place(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    await FSMPoll.place.set()
    await callback.message.answer("Где хотите отдохнуть? ⛰", reply_markup=ReplyKeyboardRemove())


async def poll_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["place"] = message.text

    await FSMPoll.next()
    await message.answer("Когда планируете отдых? Напишите конкретные даты или примерные 📆")


async def poll_duration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["time"] = message.text

    await FSMPoll.next()
    await message.answer("На сколько дней поедете?")


async def poll_number_of_person(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["duration"] = message.text

    await FSMPoll.next()
    await message.answer("Сколько Вас человек: взрослых, детей? 👨‍👩‍👧")


async def poll_hotel(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["number_of_person"] = message.text

    await FSMPoll.next()
    await message.answer("Уже выбрали отель?\n"
                         "🏡 Если да, то какой?")


async def poll_hotel_details(message: types.Message):
    await message.answer("Расскажите о Ваших пожеланиях к отелю.")


async def poll_transfer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["hotel"] = message.text

    await FSMPoll.next()
    await message.answer("Уже решили, как будете добираться?\n"
                         "🚌 Нужен трансфер?", reply_markup=yes_no_keyboard)


async def poll_transfer_details(message: types.Message):
    await message.answer("Расскажите о Ваших пожеланиях к отелю.")


async def poll_wishes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['transfer'] = message.text

    await FSMPoll.next()
    await message.answer("Есть ли дополнительные пожелания? Может я не спросил про что-то важное для Вас?",
                         reply_markup=ReplyKeyboardRemove())


async def poll_final(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    async with state.proxy() as data:
        data["wishes"] = message.text

    await state.finish()
    await message.answer(
        "Спасибо, уже работаю над Вашим отдыхом и в ближайшее время направлю лучшие варианты! До встречи!")

    about_order = (f"   Место поездки: {data['place']}\n"
                   f"   Дата поездки: {data['time']}\n"
                   f"   Продолжительность: {data['duration']}\n"
                   f"   Количество персон: {data['number_of_person']}\n"
                   f"   Отель: {data['hotel']}\n"
                   f"   Трансфер: {data['transfer']}\n"
                   f"   Дополнительные пожелания: {data['wishes']}\n")

    order = Order(user_id=user.chat_id,
                  about_order=about_order,
                  create_date=datetime.datetime.utcnow())

    await update_order(order, session)

    order_text = (f"Пользователь @{user.username} оставил заявку:\n"
                  f"   Имя: {user.name}\n"
                  f"   Телефон: {user.phone_number}\n"
                  f"   Почта: {user.email}\n\n"
                  f"О заявке:\n" +
                  about_order)

    query = select(User).filter(User.role == "Worker")

    workers = (await session.execute(query)).scalars()

    for worker in workers:
        await message.bot.send_message(worker.chat_id, md.quote_html(order_text),
                                       reply_markup=create_keyboard_inline(
                                           [Button("Взять заявку",
                                                   callback_data_order.new(id=order.order_id, action="take"))]
                                       ))


def register_questionnaire(dp: Dispatcher):
    dp.register_message_handler(make_order, Text("Заявка"), chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(make_order, commands=["order"], chat_type=types.ChatType.PRIVATE, state="*")

    dp.register_callback_query_handler(poll_place, callback_data_make_order.filter(type="poll"), state="*")
    dp.register_callback_query_handler(voice_start, callback_data_make_order.filter(type="voice"), state="*")

    dp.register_message_handler(get_voice, state=FSMVoice.voice, content_types=[ContentType.VOICE])

    dp.register_message_handler(poll_time, NotCommandFilter(), state=FSMPoll.place)
    dp.register_message_handler(poll_duration, NotCommandFilter(), state=FSMPoll.time)
    dp.register_message_handler(poll_number_of_person, NotCommandFilter(), state=FSMPoll.duration)
    dp.register_message_handler(poll_hotel, NotCommandFilter(), state=FSMPoll.number_of_persons)
    dp.register_message_handler(poll_hotel_details, NegativeAnswer(), state=FSMPoll.hotel)
    dp.register_message_handler(poll_transfer, NotCommandFilter(), state=FSMPoll.hotel)
    dp.register_message_handler(poll_transfer_details, Text("Да"), state=FSMPoll.transfer)
    dp.register_message_handler(poll_wishes, NotCommandFilter(), state=FSMPoll.transfer)
    dp.register_message_handler(poll_final, NotCommandFilter(), state=FSMPoll.wishes)
