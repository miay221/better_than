from asgiref.sync import async_to_sync
from django.shortcuts import render
from django.http import JsonResponse
import json
from .final_model import predict_emotion_async

def analyze_message(request):
    if request.method == 'POST':
        print("POST 요청 받음")
        data = json.loads(request.body)
        message = data.get('message')
        print('받은 메시지:', message)

        if message:
            # 세션에 메시지 저장 (동기 방식)
            request.session['user_message'] = message
            print('세션에 저장된 메시지:', message)

            # 비동기로 머신러닝 모델 호출
            result = async_to_sync(predict_emotion_async)(message)
            print('모델 분석 결과:', result)

            # 결과를 세션에 저장 (동기 방식)
            request.session['analysis_result'] = result

            # 분석 결과와 함께 응답 반환
            return JsonResponse({
                'status': 'success',
                'result': result,
                'redirect_url': '/chatbot/'
            })

        return JsonResponse({'status': 'error', 'message': 'No message provided'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def index(request):
    # 세션에서 메시지와 분석 결과 가져오기
    message = request.session.pop('user_message', None)
    result = request.session.pop('analysis_result', None)

    return render(request, 'chatbot/index.html', {
        'message': message,
        'result': result
    })
