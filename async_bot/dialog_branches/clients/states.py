from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMGreeting(StatesGroup):
    name = State()
    phone_number = State()
    email = State()


class FSMPoll(StatesGroup):
    place = State()
    time = State()
    duration = State()
    number_of_persons = State()
    hotel = State()
    transfer = State()
    wishes = State()


class FSMVoice(StatesGroup):
    voice = State()


class FSMChangeName(StatesGroup):
    name = State()


class FSMChangePhoneNumber(StatesGroup):
    phone_number = State()


class FSMChangeEmail(StatesGroup):
    email = State()
