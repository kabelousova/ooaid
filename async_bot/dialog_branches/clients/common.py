from aiogram import types, Dispatcher, md
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from async_bot.dialog_branches.clients.states import FSMChangeName, FSMChangeEmail, FSMChangePhoneNumber
from async_bot.dialog_branches.utils import get_number
from async_bot.filters.NotCommandFilter import NotCommandFilter
from database.crud import update_user
from database.models import User
from email_validator import validate_email, EmailNotValidError


async def command_help(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer("Я пока умею не много, я только учусь:\n\n"

                         "/order - оставить заявку на планирование Вашего отдыха\n"
                         "Или можете просто написать <b>Заявка</b>\n\n"

                         "<b>Профиль</b>\n"
                         "/profile - посмотреть профиль\n"
                         "/name - изменить имя\n"
                         "/phone - изменить номер телефона\n"
                         "/email - изменить почту\n",
                         reply_markup=ReplyKeyboardRemove())


async def command_change_name(message: types.Message):
    await message.answer("Как к вам обращаться?", reply_markup=ReplyKeyboardRemove())
    await FSMChangeName.name.set()


async def change_name_end(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    user.name = message.text

    await update_user(user, session)

    await message.answer(f"Хорошо, {md.quote_html(user.name)}.")
    await state.finish()


async def command_change_phone_number(message: types.Message):
    await message.answer("Введите Ваш новый номер.", reply_markup=ReplyKeyboardRemove())

    await FSMChangePhoneNumber.phone_number.set()


async def change_phone_number_end(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    phone_number = get_number(message.text)

    if phone_number is not None:
        user.phone_number = phone_number.national_number
        await update_user(user, session)

        await message.answer("Номер успешно обновлен.")
        await state.finish()
    else:
        await message.answer("Мне кажется, таких телефонов не бывает.\n\n"
                             "Давайте проверим 😊")


async def command_change_email(message: types.Message):
    await message.answer("Введите Вашу новую почту.", reply_markup=ReplyKeyboardRemove())

    await FSMChangeEmail.email.set()


async def change_email_end(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    try:
        email = validate_email(message.text).email

        user.email = email
        await update_user(user, session)
        await message.answer("Почта успешно обновлена.")
        await state.finish()
    except EmailNotValidError:
        await message.answer("Мне кажется, таких адресов не бывает.\n\n"
                             "Давайте проверим 😊")


async def command_sales(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>Акция</b>\n"
                         "\n"
                         "Оформи через меня тур за три дня и получи скидку <b>5%</b>!\n"
                         "\n"
                         "<b>Что нужно сделать?</b>\n"
                         "  👉 Оставить мне заявку на подбор тура\n"
                         "  👉 В течении трех дней после получения предложенного варианта оформить тур",
                         reply_markup=ReplyKeyboardRemove())


async def command_news(message: types.Message, state: FSMContext):
    await state.finish()
    with open("./files/image/hotel.png", 'rb') as image:
        await message.answer_photo(photo=image,
                                   caption="💥 <b>Гарантированные места в санаториях Белокурихи на Новый Год</b>\n"
                                           "\n"
                                           "🏩 <b>Санаторий «Россия»</b>\n"
                                           "✔️<b>24.12.2022 - 08.01.2023</b>\n"
                                           "2 номера «Стандарт 1-местный» - от 8500 чел./сутки\n"
                                           "Четырехразовое питание и лечение включено в стоимость\n"
                                           "📌 <b>Подробнее</b>: https://www.ohotka.ru/region/belokuriha/sanatorii-gostiniczy/rossiya-sanatorij/\n"
                                           "\n"
                                           "🏩 <b>Санаторий «Алтайский Замок»</b>\n"
                                           "✔️<b>24.12.2022 - 08.01.2023</b>\n"
                                           "2 номера «Комфорт 2-местный» - от 5650 чел./сутки\n"
                                           "Трехразовое питание и лечение включено в стоимость\n"
                                           "📌 <b>Подробнее</b>: https://www.ohotka.ru/region/belokuriha/sanatorii-gostiniczy/altajskij-zamok-sanatorij/\n"
                                           "\n"
                                           "🏩 <b>Санаторий «Сибирь»</b>\n"
                                           "✔️<b>25.12.2022-08.01.2023</b>\n"
                                           "Номер «Комфорт 2-местный» - от 5600 чел./сутки\n"
                                           "Номер «Стандарт 2-местный» - от 5400 чел./сутки\n"
                                           "Номер «Стандарт 1-местный» - от 6900 чел./сутки\n"
                                           "Трехразовое питание и лечение включено в стоимость\n"
                                           "📌 <b>Подробнее</b>: https://www.ohotka.ru/region/belokuriha/sanatorii-gostiniczy/sibir-sanatorij/",
                                   reply_markup=ReplyKeyboardRemove())

    with open("./files/image/cashback.png", 'rb') as image:
        await message.answer_photo(photo=image,
                                   caption="🥳 <b>Кэшбэк стартует сегодня!</b>\n"
                                           "\n"
                                           "📌 Сроки проведения программы: <b>25.08.2022-10.09.2022</b>\n"
                                           "📌 Период заезда: <b>01.10.2022-25.12.2022</b>\n"
                                           "\n"
                                           "✅ <b>Условия начисления:</b>\n"
                                           "- минимальная продолжительность 3 ночи/4 дня\n"
                                           "- территория – вся Россия\n"
                                           "- возврат 20% от суммы покупки, но не более 20 тыс.рублей за одну транзакцию\n"
                                           "👉 <b>Подробнее</b>: https://www.ohotka.ru/about/action/novyj-etap-programmy-keshbek/",
                                   reply_markup=ReplyKeyboardRemove())


async def command_creator(message: types.Message):
    await message.answer("Создатели бота: @ka_belousova.",
                         reply_markup=ReplyKeyboardRemove())


async def show_profile_info(message: types.Message, user: User, state: FSMContext):
    await state.finish()

    text = f"<b>Профиль</b>\n\n" \
           f"Имя: {user.name}\n" \
           f"Телефон: {'+7' + str(user.phone_number) if user.phone_number is not None else 'Нет'}\n" \
           f"Почта: {user.email if user.email is not None else 'Нет'}\n"

    await message.answer(text)


def register_common(dp: Dispatcher):
    dp.register_message_handler(command_help, commands=['help'], state="*", chat_type=types.ChatType.PRIVATE)

    dp.register_message_handler(command_sales, commands=['sales'], state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(command_news, commands=['news'], state="*", chat_type=types.ChatType.PRIVATE)

    dp.register_message_handler(command_creator, commands=['creator'], state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(show_profile_info, commands=['profile'], state="*", chat_type=types.ChatType.PRIVATE)

    dp.register_message_handler(command_change_name, commands=['name'], state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(change_name_end, NotCommandFilter(), state=FSMChangeName.name)

    dp.register_message_handler(command_change_phone_number, commands=['phone'], state="*",
                                chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(change_phone_number_end, NotCommandFilter(), state=FSMChangePhoneNumber.phone_number)

    dp.register_message_handler(command_change_email, commands=['email'], state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(change_email_end, NotCommandFilter(), state=FSMChangeEmail.email)
