from sqlalchemy.future import select

from database.models import User, UserOrders, Order


async def get_user_by_id(chat_id: int, session) -> User:
    query = select(User).filter(User.chat_id == chat_id)

    return (await session.execute(query)).scalars().first()


async def get_all_users(session):
    query = select(User)

    return (await session.execute(query)).scalars()


async def get_user_by_username(username: str, session) -> User:
    query = select(User).filter(User.username == username)

    return (await session.execute(query)).scalars().first()


async def update_user(user: User, session) -> User:
    session.add(user)
    await session.commit()
    return user


async def update_order(order: Order, session) -> Order:
    session.add(order)
    await session.commit()
    return order


async def get_order(order_id: int, session) -> Order:
    query = select(Order).filter(Order.order_id == order_id)

    return (await session.execute(query)).scalars().first()


async def get_took_order(order_id: int, chat_id, session) -> UserOrders:
    query = select(UserOrders).filter(UserOrders.order_id == order_id, UserOrders.manager_id == chat_id,
                                      UserOrders.close_date == None)

    return (await session.execute(query)).scalars().first()
