from asgiref.sync import async_to_sync
from django.shortcuts import render
from django.http import JsonResponse
import json
from .final_model import predict_emotion_async, generate_lime_explanation
import random


def random_num(end):
    return random.randint(1, end)

def analyze_message(request):
    if request.method == 'POST':

        card_texts_list = ["내 기분은 내가 정할래. 오늘의 나는 '행복'이야",
                      "불가능한 것을 이루는 유일한 방법은 가능하다고 믿는거야",
                      "넌 틀림없이 도착하게 될 거야. 계속 걷다보면 어디든 닿게 되거든",
                      "모든 모험은 첫 걸음을 필요로 한대",
                      "과거를 바꿀 순 없지만 교훈을 얻을 수 있을거야",
                      "그래 넌 미쳤어. 이건 비밀인데...멋진 사람들은 다 미쳤단다!",
                      "지도만 보면 뭐하겠어? 남이 만들어 놓은 지도에 네가 가고 싶은 길은 없어. 넌 너만의 지도를 만들어야 해",
                      "가장 예쁜 꽃은 언제나 가장 멀리 있단다",
                      "지금의 넌 어제의 네가 아니야. 그러니까 어제의 이야기는 아무 의미가 없어"
                      ]

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

            values=result['probabilities']
            max_val= max([round(val, 2) for val in values[0]])
            print('가장 높은 확률', max_val)

            range_values = list(range(result['predicted_class']))
            range_values.append(result['predicted_class'] + 1)  # 마지막 값에 1 추가
            print('예측된 클래스:', range_values)

            clover_cnt = len(range_values) # 클로버 이미지 갯수 (예측 클래스)
            card_texts_cnt = len(card_texts_list)
            random_number = random_num(card_texts_cnt)
            card_texts = card_texts_list[random_number - 1]


            # 비동기로 Lime 결과 생성
            lime_explainer_html = async_to_sync(generate_lime_explanation)(message)

            # 결과를 세션에 저장 (동기 방식)
            request.session['analysis_result'] = result
            request.session['max_val'] = max_val
            request.session['range'] = range_values
            request.session['lime_explainer'] = lime_explainer_html
            request.session['clover_cnt'] = clover_cnt
            request.session['card_texts'] = card_texts

            # 분석 결과, 응답 반환
            return JsonResponse({
                'status': 'success',
                'result': result,
                'lime_explainer' : lime_explainer_html,
                'redirect_url': '/chatbot/'
            })

        return JsonResponse({'status': 'error', 'message': 'No message provided'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




def index(request):
    # 세션에서 메시지와 분석 결과 가져오기
    message = request.session.get('user_message', None)
    result = request.session.get('analysis_result', None)
    max_val = request.session.get('max_val', None)
    range_values = request.session.get('range', None)
    lime_explainer = request.session.get('lime_explainer', None)
    clover_cnt = request.session.get('clover_cnt', None)
    card_texts = request.session.get('card_texts', None)

    return render(request, 'chatbot/index.html', {
        'message': message,
        'result': result,
        'max_val': max_val,
        'range':range_values,
        'lime_explainer':lime_explainer,
        'clover_cnt':clover_cnt,
        'card_texts':card_texts,
    })

