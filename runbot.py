import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.core.management.base import BaseCommand
from google import genai
from google.genai import types as genai_types

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8859225888:AAEPPzQmiKZtfz-y3Wk2stHWmeh48OA6GmA"
GEMINI_API_KEY = "AIzaSyDKNGQ4wZ6ehjRy3lv8cKXar7KLYpBavWo"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

client = genai.Client(api_key=GEMINI_API_KEY)

class HomeworkState(StatesGroup):
    waiting_for_photo = State()

SYSTEM_PROMPT = """
!Ты — умный помощник по решению домашних заданий (ГДЗ). 
Давай подробное пошаговое решение с формулами и логикой.
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Отправь мне фото страницы с заданием, и я найду или решу его!"
    )
    await state.set_state(HomeworkState.waiting_for_photo)

@dp.message(HomeworkState.waiting_for_photo, F.photo)
async def handle_homework_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
    
    processing_msg = await message.answer("Анализирую задание...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                image_bytes = await resp.read()

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                genai_types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                "Реши это домашнее задание пошагово."
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1500,
            )
        )
        
        answer_text = response.text
        
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        await message.answer(answer_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка при работе с Gemini: {e}")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        except:
            pass
        await message.answer("Произошла ошибка при обработке запроса.")

@dp.message(HomeworkState.waiting_for_photo)
async def not_photo(message: types.Message):
    await message.answer("Пожалуйста, отправь именно **фотографию** задания.")

async def main():
    await dp.start_polling(bot)

class Command(BaseCommand):
    help = 'Запуск Telegram-бота для ГДЗ через Gemini'

    def handle(self, *args, **options):
        asyncio.run(main())