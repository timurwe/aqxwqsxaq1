import os
import django
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai
from google.genai import types as genai_types
from dotenv import load_dotenv

load_dotenv() 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_gemini_client():
    """Безопасное создание клиента Gemini при вызове"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing or empty!")
    return genai.Client(api_key=api_key)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 🤖 Я твой ИИ-помощник по ГДЗ.\n\n"
        "📸 **Отправь мне фото с заданием**, текстом или напиши условие (например: *Алгебра 7 класс номер 15*), "
        "и я помогу тебе разобраться!",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.photo is not None)
async def handle_photo(message: types.Message):
    await message.answer("🔍 Читаю фото и решаю задачу, подожди секунду...")
    
    try:
        client = get_gemini_client()
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        
        downloaded_file = await bot.download_file(file_path)
        temp_filename = "temp_task.jpg"
        with open(temp_filename, "wb") as f:
            f.write(downloaded_file.read())
            
        uploaded_file = client.files.upload(file=temp_filename)
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[
                uploaded_file,
                "Реши эту задачу пошагово. Объясни каждый шаг понятным языком для школьника."
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction="!Ты — умный помощник по учебе. Пиши понятные пошаговые решения на русском языке.",
                max_output_tokens=1500,
            )
        )
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        await message.answer(f"💡 **Решение по фото:**\n\n{response.text}", parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка при обработке фото: {str(e)}")

@dp.message()
async def search_homework(message: types.Message):
    query_text = message.text.lower()
    
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[f"Помоги решить школьное задание: {query_text}. Дай подробное пошаговое решение."],
            config=genai_types.GenerateContentConfig(
                system_instruction="!Ты — умный помощник по учебе. Пиши понятные пошаговые решения.",
                max_output_tokens=1500,
            )
        )
        await message.answer(f"🤖 **Ответ ИИ:**\n\n{response.text}", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"🤔 Не удалось обработать запрос: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())