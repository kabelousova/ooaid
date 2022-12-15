from aiogram import Dispatcher

from async_bot.dialog_branches.admins import register_admin_handlers
from async_bot.dialog_branches.clients import register_client_handlers
from async_bot.dialog_branches.start import register_start_handlers
from async_bot.dialog_branches.workers import register_worker_handlers


def register_branches(dp: Dispatcher):
    register_start_handlers(dp)
    register_client_handlers(dp)
    register_admin_handlers(dp)
    register_worker_handlers(dp)
