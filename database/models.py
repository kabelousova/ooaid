from os import getenv

from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, MetaData, Text, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),

    # Именование индексов
    'ix': 'ix__%(table_name)s__%(all_column_names)s',

    # Именование уникальных индексов
    'uq': 'uq__%(table_name)s__%(all_column_names)s',

    # Именование CHECK-constraint-ов
    'ck': 'ck__%(table_name)s__%(constraint_name)s',

    # Именование внешних ключей
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',

    # Именование первичных ключей
    'pk': 'pk__%(table_name)s'
}
Base.metadata = MetaData(naming_convention=convention)


class User(Base):
    __tablename__ = 'user'

    chat_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(String, unique=True, nullable=True)

    name = Column(String(100), nullable=True)
    phone_number = Column(BigInteger, nullable=True)
    email = Column(String(100), nullable=True)
    role = Column(String(100), nullable=False, default='Client')
    register_date = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f'User(name={self.name}, phone_number={self.phone_number}, email={self.email}, role={self.role})'


class Order(Base):
    __tablename__ = 'order'

    order_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.chat_id), nullable=False)
    about_order = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)


class UserOrders(Base):
    __tablename__ = 'user_orders'

    order_id = Column(BigInteger, ForeignKey(Order.order_id), primary_key=True, unique=True)
    manager_id = Column(BigInteger, ForeignKey(User.chat_id), nullable=False)
    close_date = Column(DateTime, nullable=True)


def get_sessionmaker() -> sessionmaker:
    user = getenv('POSTGRES_USER')
    password = getenv('POSTGRES_PASSWORD')

    engine = create_async_engine(f'postgresql+asyncpg://ohotkin:ohota_travel@165.22.68.78:5432/ohotkin-bot', echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session
