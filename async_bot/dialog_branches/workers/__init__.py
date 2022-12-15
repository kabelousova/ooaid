from aiogram import Dispatcher

from async_bot.dialog_branches.workers.callback import take_order, close_order, register_worker_callback_handlers


def register_worker_handlers(dp: Dispatcher):
    register_worker_callback_handlers(dp)
