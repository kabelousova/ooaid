from aiogram import Dispatcher

from async_bot.dialog_branches.admins.admin_menu import register_admin_menu_handlers
from async_bot.dialog_branches.admins.add_worker import register_add_worker_handlers
from async_bot.dialog_branches.admins.delete_worker import register_delete_worker_handlers
from async_bot.dialog_branches.admins.get_statistic import register_statistic_handlers
from async_bot.dialog_branches.admins.show_workers import register_show_workers_handlers


def register_admin_handlers(dp: Dispatcher):
    register_admin_menu_handlers(dp)
    register_delete_worker_handlers(dp)
    register_add_worker_handlers(dp)
    register_statistic_handlers(dp)
    register_show_workers_handlers(dp)
