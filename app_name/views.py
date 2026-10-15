from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types as genai_types
import os
import traceback
from dotenv import load_dotenv

load_dotenv()  

def home(request):
    """Отрисовка главной страницы веб-приложения (Telegram Mini App)"""
    return render(request, 'index.html')

@csrf_exempt
def solve_homework_api(request):
    """API-эндпоинт для решения домашних заданий по текстам или фотографиям"""
    if request.method == 'POST':
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({
                    'success': False, 
                    'error': 'GEMINI_API_KEY environment variable is missing or empty!'
                }, status=500)
            
            client = genai.Client(api_key=api_key)

            if request.FILES.get('image'):
                image_file = request.FILES['image']
                temp_path = f"temp_{image_file.name}"
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                uploaded_file = client.files.upload(file=temp_path)
                
                user_comment = request.POST.get('task', 'Реши эту задачу пошагово. Объясни каждый шаг понятным языком.')

                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[uploaded_file, user_comment],
                    config=genai_types.GenerateContentConfig(
                        system_instruction="!Ты — умный помощник по учебе. Пиши понятные пошаговые решения на русском языке.",
                        max_output_tokens=1500,
                    )
                )
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                return JsonResponse({'success': True, 'solution': response.text})
            
            else:
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    data = request.POST

                subject = data.get('subject', '')
                grade = data.get('grade', '')
                task = data.get('task', '')

                if not task:
                    return JsonResponse({'success': False, 'error': 'Текст задания не передан'}, status=400)

                prompt = f"Предмет: {subject}, класс: {grade}. Задание: {task}. Дай подробное пошаговое решение."

                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[prompt],
                    config=genai_types.GenerateContentConfig(
                        system_instruction="!Ты — умный помощник по учебе. Пиши понятные пошаговые решения на русском языке.",
                        max_output_tokens=1500,
                    )
                )

                return JsonResponse({'success': True, 'solution': response.text})
        
        except Exception as e:
            error_details = traceback.format_exc()
            print("ОШИБКА В API SOLVE:", error_details)
            return JsonResponse({
                'success': False, 
                'error': str(e),
                'trace': error_details
            }, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)