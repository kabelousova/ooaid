from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMAdminMenu(StatesGroup):
    menu = State()
    add = State()
    delete = State()
    broadcast = State()
