from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMForwardMessage(StatesGroup):
    forward = State()
