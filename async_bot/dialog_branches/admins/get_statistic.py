from aiogram import types, Dispatcher, md
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from async_bot.dialog_branches.admins.states import FSMAdminMenu
from database.models import UserOrders, Order, User


def days_hours_minutes(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60


async def statistic(message: types.Message, session: AsyncSession):
    query = select(func.avg(UserOrders.close_date - Order.create_date)) \
        .select_from(UserOrders).join(Order, Order.order_id == UserOrders.order_id)

    avg_response = days_hours_minutes((await session.execute(query)).scalars().first())

    await message.answer(f"<b>Среднее время ответа на заявку:</b>\n"
                         f" {avg_response[0]} дней, {avg_response[1]} часов, {avg_response[2]} минут")

    query = select(User.username, User.name, func.count(),
                   func.avg(UserOrders.close_date - Order.create_date)).select_from(User) \
        .join(UserOrders, User.chat_id == UserOrders.manager_id) \
        .join(Order, Order.order_id == UserOrders.order_id).group_by(User.username, User.name)

    text = "<b>Статистика по обработанным заявкам:</b>\n"

    statistic_managers = (await session.execute(query))
    for manager in statistic_managers:
        mean_time = days_hours_minutes(manager[3])
        text += f"\n" \
                f"Телеграм: {manager[0]}\n" \
                f"Имя: {md.quote_html(manager[1])}\n" \
                f"Количество обработанных заявок: {manager[2]} \n" \
                f"Среднее время ответа на заявку: {mean_time[0]} дней, {mean_time[1]} часов, {mean_time[2]} минут\n"

    await message.answer(text)


def register_statistic_handlers(dp: Dispatcher):
    dp.register_message_handler(statistic, commands=['statistic'], state=FSMAdminMenu.menu)
