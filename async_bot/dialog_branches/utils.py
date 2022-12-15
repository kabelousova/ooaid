import os
import subprocess

import phonenumbers
import speech_recognition as sr
from collections import namedtuple
from typing import List

from aiogram.bot import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Voice
from aiogram.utils.callback_data import CallbackData
from phonenumbers import PhoneNumber

Button = namedtuple("Button", ["name", "data"])

callback_data_order = CallbackData("order", "action", "id")
callback_data_make_order = CallbackData("make_order", "type")
callback_data_leave_order = CallbackData("leave_order", "answer")


def create_keyboard_reply(names: List[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    for name in names:
        keyboard.add(KeyboardButton(name))

    return keyboard


def create_keyboard_inline(buttons: List[Button]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)

    for button in buttons:
        keyboard.add(InlineKeyboardButton(button.name, callback_data=button.data))

    return keyboard


async def convert_voice(voice: Voice, bot: Bot) -> str:
    path = "./files/voices"

    try:
        await bot.download_file_by_id(voice.file_id, f"{path}/{voice.file_id}.ogg", make_dirs=False)
        subprocess.run(["ffmpeg", "-nostdin", "-i", f"{path}/{voice.file_id}.ogg", f"{path}/{voice.file_id}.wav"])

        return audio_to_text(f"{path}/{voice.file_id}.wav")
    finally:
        os.remove(f"{path}/{voice.file_id}.ogg")
        os.remove(f"{path}/{voice.file_id}.wav")


def audio_to_text(dest_name: str):
    r = sr.Recognizer()

    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")

    return result


def get_number(phone_number: str) -> PhoneNumber:
    try:
        phone_number = phonenumbers.parse(phone_number, "RU")

        if phonenumbers.is_valid_number(phone_number):
            return phone_number
        else:
            return None
    except:
        return None
