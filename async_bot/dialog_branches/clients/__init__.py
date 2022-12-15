from aiogram import Dispatcher

from async_bot.dialog_branches.clients.common import register_common
from async_bot.dialog_branches.clients.greeting import register_greeting
from async_bot.dialog_branches.clients.questionnaire import register_questionnaire


def register_client_handlers(dp: Dispatcher):
    register_common(dp)
    register_greeting(dp)
    register_questionnaire(dp)
