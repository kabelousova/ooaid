import asyncio
import datetime
import time

from aiogram import Bot
from sqlalchemy.orm import sessionmaker

from database.crud import get_all_users


async def news_notification(bot: Bot, s_maker: sessionmaker):
    await asyncio.sleep(3)
    if datetime.datetime.fromtimestamp(time.time()) > datetime.datetime(2022, 8, 29):
        return

    async with s_maker() as session:
        users = await get_all_users(session)

        for user in users:
            try:
                with open("./files/image/hotel.png", 'rb') as image1:
                    await bot.send_photo(user.chat_id,
                                         photo=image1,
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
                                                 "📌 <b>Подробнее</b>: https://www.ohotka.ru/region/belokuriha/sanatorii-gostiniczy/sibir-sanatorij/")

                with open("./files/image/cashback.png", 'rb') as image2:
                    await bot.send_photo(user.chat_id,
                                         photo=image2,
                                         caption="🥳 <b>Кэшбэк стартует сегодня!</b>\n"
                                                 "\n"
                                                 "📌 Сроки проведения программы: <b>25.08.2022-10.09.2022</b>\n"
                                                 "📌 Период заезда: <b>01.10.2022-25.12.2022</b>\n"
                                                 "\n"
                                                 "✅ <b>Условия начисления:</b>\n"
                                                 "- минимальная продолжительность 3 ночи/4 дня\n"
                                                 "- территория – вся Россия\n"
                                                 "- возврат 20% от суммы покупки, но не более 20 тыс.рублей за одну транзакцию\n"
                                                 "👉 <b>Подробнее</b>: https://www.ohotka.ru/about/action/novyj-etap-programmy-keshbek/")
            except:
                pass
