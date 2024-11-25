from django.shortcuts import render
from django.http import JsonResponse
from .models import Feedback
import json

def index(request):
    return render(request, 'home/index.html')


def qr(request):
    return render(request, 'home/qr.html')

def save_feedback(request):
    if request.method == 'POST':
        try:
            # 요청에서 JSON 데이터 읽기
            data = json.loads(request.body)
            feedback_text = data.get('feedback')  # 'feedback' 키로 데이터 가져옴
            print('feedback_text:', feedback_text)

            if feedback_text:  # 내용이 있다면
                # 모델 객체 생성 및 저장
                Feedback.objects.create(feedback_text=feedback_text)
                return JsonResponse({'status': 'success', 'message': 'Feedback saved! thank you'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No feedback'}, status=400)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)