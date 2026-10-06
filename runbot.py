import subprocess
import sys

def run_services():
    print("🚀 Запуск миграций базы данных...")
    subprocess.run([sys.executable, "manage.py", "migrate"])

    print("🤖 Запуск Telegram-бота и сервера...")
    bot_process = subprocess.Popen([sys.executable, "bot.py"])
    uvicorn_process = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])

    try:
        bot_process.wait()
        uvicorn_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Остановка проекта...")
        bot_process.terminate()
        uvicorn_process.terminate()

if __name__ == "__main__":
    run_services()




#8859225888:AAEPPzQmiKZtfz-y3Wk2stHWmeh48OA6GmA