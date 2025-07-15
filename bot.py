import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import re
from db import add_birthday, get_all_birthdays, get_birthdays_by_date, delete_birthday_by_id

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Нет токена бота. Добавьте BOT_TOKEN в .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу тебе хранить дни рождения друзей. Для справки используй /help.")


@dp.message(Command(commands=["add"]))
async def add_birthday_handler(message: Message):

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Неверный формат. Используй: /add Описание ДД-ММ")
        return

    description = args[1].strip()
    date_str = args[2].strip()

    # Проверка описания
    if not description:
        await message.answer("Описание не может быть пустым.")
        return

    # Валидация даты (ДД-ММ)
    if not re.match(r"^\d{2}-\d{2}$", date_str):
        await message.answer("Дата должна быть в формате ДД-ММ")
        return

    day, month = map(int, date_str.split("-"))
    if not (1 <= day <= 31 and 1 <= month <= 12):
        await message.answer("Некорректная дата. Проверь день и месяц.")
        return

    user_id = message.from_user.id
    add_birthday(user_id, date_str, description)
    await message.answer(f"Добавлено: {description} — {date_str}")



@dp.message(Command("list"))
async def list_birthdays(message: Message):
    user_id = message.from_user.id
    events = get_all_birthdays(user_id)
    if not events:
        await message.answer("Список событий пуст.")
        return
    text = "Твои события:\n" + "\n".join(
        [f"{desc} — {date}" for desc, date in events]
    )
    await message.answer(text)


@dp.message(Command("delete"))
async def delete_birthday(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Формат: /delete ДД-ММ\nПример: /delete 15-07")
        return
    date_str = args[1].strip()
    user_id = message.from_user.id
    events = get_birthdays_by_date(user_id, date_str)
    if not events:
        await message.answer(f"Событий на дату {date_str} не найдено.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=descr, callback_data=f"del_{event_id}")]
            for event_id, descr in events
        ]
    )
    await message.answer(
        "Выбери событие для удаления:",
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data.startswith("del_"))
async def process_delete_callback(callback_query):
    event_id = int(callback_query.data.split("_")[1])
    delete_birthday_by_id(event_id)
    await callback_query.message.edit_text("Событие удалено.")

@dp.message(Command("help"))
async def help_command(message: Message):
    text = (
        "/add Имя ДД-ММ — добавить новое событие\n"
        "/list — посмотреть все сохранённые события\n"
        "/delete ДД-ММ — удалить событие по дате\n"
        "/help — эта справка"
    )
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    from db import init_db
    init_db()
    asyncio.run(main())
