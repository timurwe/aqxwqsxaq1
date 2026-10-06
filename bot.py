import os
import django
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdz_project.settings')

from app_name.models import Textbook, Task  

API_TOKEN = '8859225888:AAEPPzQmiKZtfz-y3Wk2stHWmeh48OA6GmA' 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 🤖 Я твой ИИ-помощник по ГДЗ.\n\n"
        "Отправь мне название предмета, учебника и номер задания (например: *Алгебра 7 класс номер 15*), "
        "или задай вопрос по сложной теме, и я помогу тебе разобраться!",
        parse_mode="Markdown"
    )

@dp.message()
async def search_homework(message: types.Message):
    query_text = message.text.lower()
    
    tasks = Task.objects.filter(number__icontains=query_text) | Task.objects.filter(solution_text__icontains=query_text)
    
    if tasks.exists():
        response = "📚 **Найденные решения:**\n\n"
        for task in tasks[:3]:  
            response = response + f"📖 *Учебник:* {task.textbook.title}\n"
            response = response + f"📝 *Задание №{task.number}*\n"
            response = response + f"💡 *Решение:* {task.solution_text[:300]}...\n\n"
        await message.answer(response, parse_mode="Markdown")
    else:
        await message.answer(
            "🤔 В моей базе пока нет готового ответа на это задание. "
            "Но я могу объяснить тему, если ты опишешь условие задачи подробнее!"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())