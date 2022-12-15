import datetime
from typing import Dict

from aiogram import types, Dispatcher, md
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from async_bot.dialog_branches.utils import create_keyboard_inline, callback_data_order, Button
from async_bot.dialog_branches.workers.states import FSMForwardMessage
from database.crud import get_took_order
from database.models import User, UserOrders, Order


async def take_order(callback: types.CallbackQuery, callback_data: Dict[str, str], state: FSMContext,
                     session: AsyncSession, user: User):
    order_id = int(callback_data["id"])
    await callback.answer()

    query_already_took = select(UserOrders).filter(UserOrders.order_id == order_id,
                                                   UserOrders.manager_id != user.chat_id)
    query_not_closed = select(UserOrders).filter(UserOrders.manager_id == user.chat_id, UserOrders.close_date == None)

    order_already_took = (await session.execute(query_already_took)).scalars().first()
    order_not_closed = (await session.execute(query_not_closed)).scalars().first()

    if order_already_took:
        await callback.message.answer("Данная заявка уже взята или закрыта другим сотрудником")
        await callback.message.delete()

    elif order_not_closed:
        await callback.message.answer("У вас есть незакрытая заявка, закройте ее сначала")
    else:
        await callback.message.delete_reply_markup()

        await callback.message.answer(
            "Вы взяли заявку. Теперь каждое ваше сообщение будет пересылаться клиенту. "
            "Будьте аккуратны. Чтобы закрыть заявка нажмите кнопку \"Закрыть заявку\". "
            "Вы можете отправлять любые ссылки, фотографии и текст.",
            reply_markup=create_keyboard_inline(
                [Button("Закрыть заявку", callback_data_order.new(id=order_id, action="close"))])
        )

        user_order = UserOrders(order_id=order_id, manager_id=user.chat_id)
        session.add(user_order)

        await FSMForwardMessage.forward.set()
        query = select(Order).filter(Order.order_id == order_id)
        order = (await session.execute(query)).scalars().first()

        async with state.proxy() as data:
            data["forward"] = order.user_id

        await session.commit()


async def forward_message(message: types.Message, state: FSMContext, session: AsyncSession, user: User):
    async with state.proxy() as data:
        dest = data["forward"]

    try:
        await message.send_copy(dest)
    except:
        await message.answer("Ошибка отправки сообщения. Похоже, клиент заблокировал бота.")


async def close_order(callback: types.CallbackQuery, callback_data: Dict[str, str], state: FSMContext,
                      session: AsyncSession, user: User):
    order_id = int(callback_data["id"])

    await callback.answer()
    await callback.message.answer("Заявка закрыта. Теперь вы можете брать следующую заявку.")

    user_order = await get_took_order(order_id, user.chat_id, session)

    if user_order is not None:
        user_order.close_date = datetime.datetime.utcnow()

        session.add(user_order)
        await session.commit()

        query = select(Order).filter(Order.order_id == order_id)
        order = (await session.execute(query)).scalars().first()

        await callback.bot.send_message(order.user_id,
                                        "Если Вам понравился предложенный вариант или хотите его "
                                        "обсудить, можете написать моему менеджеру:\n"
                                        f"<b>{md.quote_html(user.name)}</b>\n"
                                        f"Telegram: @{md.quote_html(user.username)}")

    await state.finish()
    await callback.message.delete()


def register_worker_callback_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(take_order, callback_data_order.filter(action="take"), state='*')
    dp.register_message_handler(forward_message, state=FSMForwardMessage.forward, content_types=[ContentType.ANY])
    dp.register_callback_query_handler(close_order, callback_data_order.filter(action="close"),
                                       state=FSMForwardMessage.forward)
