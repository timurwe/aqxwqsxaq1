from google import genai

# Вставьте сюда ваш API-ключ
API_KEY = "8859225888:AAEPPzQmiKZtfz-y3Wk2stHWmeh48OA6GmA"

try:
    print("⏳ Проверяем подключение к Gemini...")
    client = genai.Client(api_key=API_KEY)
    
    # Простейший тестовый запрос
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Привет! Напиши одно слово: Работает'
    )
    
    print("✅ Успех! Ключ валидный и рабочий.")
    print("Ответ от модели:", response.text)

except Exception as e:
    print("❌ Ошибка! Ключ недействителен или произошла проблема:")
    print(str(e))