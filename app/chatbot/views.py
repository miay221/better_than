from django.shortcuts import render
from django.http import JsonResponse
import json


def index(request):
    return render(request, 'chatbot/index.html')

def save_message(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        message=data.get('message')
        if message:
            print('메시지 있음')
            request.session['user_message'] = message # 세션에 메시지 저장
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message':'No message provided'}, status=400)
    return JsonResponse({'status':'error', 'message':'Invalid request method'}, status=405)
