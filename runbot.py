import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.core.management.base import BaseCommand
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

class Command(BaseCommand):
    help = 'Запуск Telegram-бота для ГДЗ'

    def handle(self, *args, **options):
        asyncio.run(main())

TELEGRAM_TOKEN = ""
OPENAI_API_KEY = ""

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

class HomeworkState(StatesGroup):
    waiting_for_photo = State()

SYSTEM_PROMPT = """
Ты — умный помощник по решению домашних заданий (ГДЗ). 
Давай подробное пошаговое решение с формулами и логикой.
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Отправь мне фото страницы с заданием, и я найду или решу его!"
    )
    await state.set_state(HomeworkState.waiting_for_photo)

@dp.message(HomeworkState.waiting_for_photo, F.photo)
async def handle_homework_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
    
    processing_msg = await message.answer("🔍 Анализирую задание...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Реши это домашнее задание пошагово."},
                        {"type": "image_url", "image_url": {"url": file_url}}
                    ]
                }
            ],
            max_tokens=1500
        )
        
        answer_text = response.choices[0].message.content
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        
        await message.answer(answer_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.edit_text("⚠️ Произошла ошибка при обработке запроса.")

async def main():
    await dp.start_polling(bot)