from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types as genai_types

client = genai.Client(api_key="ВАШ_GEMINI_API_KEY")

@csrf_exempt
def solve_homework_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = data.get('subject')
            grade = data.get('grade')
            task = data.get('task')

            prompt = f"Предмет: {subject}, класс: {grade}. Задание: {task}. Дай подробное пошаговое решение."

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt],
                config=genai_types.GenerateContentConfig(
                    system_instruction="!Ты — умный помощник по учебе. Пиши понятные пошаговые решения.",
                    max_output_tokens=1500,
                )
            )

            return JsonResponse({'success': True, 'solution': response.text})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)