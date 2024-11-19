import re
import pandas as pd
# from google.colab import drive
import torch
from torch.nn.functional import softmax  # 0~1 사이 확률로 반환
from lime.lime_text import LimeTextExplainer
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# hugging face 저장된 모델, 토크나이저 로드
hf_model_path = "miayyyyy/downstream_kcBERT_emotionLabel"  # Hugging Face 모델 경로
tokenizer = AutoTokenizer.from_pretrained(hf_model_path)
model = AutoModelForSequenceClassification.from_pretrained(hf_model_path)

positive_words_file='./data/positive_words.csv'
negative_words_file='./data/negative_words.csv'

pos_words=pd.read_csv(positive_words_file)
neg_words=pd.read_csv(negative_words_file)


# 긍정, 부정 단어 CSV 파일 로드
positive_words = pos_words['word'].tolist()
negative_words = neg_words['word'].tolist()

# 입력 실시간 텍스트 전처리 함수
def preprocess_text(text):
    # 긍정 및 부정 단어 리스트 이용해 띄어쓰기 처리
    for word in positive_words + negative_words:
        if word in text and not f" {word} " in text:
            # 붙어있는 경우 띄어쓰기 추가
            text = text.replace(word, f" {word} ")
    text = re.sub(r'[\U0001F600-\U0001F64F]', '😊', text)  # 기본 이모티콘을 웃는 이모티콘으로 대체
    text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # 기타 심볼 이모티콘 제거
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # 운송 이모티콘 제거
    text = re.sub(r'[\U0001F700-\U0001F77F]', '', text)  # 기타 추가 심볼 제거
    text = re.sub(r'\s+', ' ', text).strip()     # 2. 과도한 공백 제거
    text = re.sub(r'([ㄱ-ㅎㅏ-ㅣ가-힣])\1{2,}', r'\1\1', text)   # 3. 자음/모음 반복 제
    text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s]', '', text)  # 한글, 영어, 숫자, 공백을 제외한 문자 제거

    return text

# 입력 텍스트에 대한 예측을 위한 함수
def predict_proba(texts):
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
    outputs = model(**inputs)
    logits = outputs.logits
    proba = torch.softmax(logits, dim=-1)
    return proba.detach().numpy()


# 사용자 텍스트 문맥 라벨 예측 함수
def predict_user_sentence(review_sentence):

  # 사용자 입력 텍스트 전처리
  user_sentence = preprocess_text(review_sentence)

  # LIME 설정 및 설명 생성
  explainer = LimeTextExplainer(class_names=[0, 1, 2, 3, 4])  # 예: 감정 라벨이 0~4로 설정됨
  explanation = explainer.explain_instance(user_sentence, predict_proba, num_features=4, num_samples=100)

  # 하이라이팅된 텍스트 시각화
  explanation.show_in_notebook(text=user_sentence)

  # 모델 예측 실행
  inputs = tokenizer(user_sentence, return_tensors="pt", truncation=True, padding=True, max_length=128)
  with torch.no_grad():
      outputs = model(**inputs)
      logits = outputs.logits

  predicted_probabilities = torch.softmax(logits, dim=-1)
  predicted_class = torch.argmax(predicted_probabilities, dim=-1).item()  # 예측된 클래스 인덱스

  # 최종 예측이 끝난 후 메모리 해제
  del inputs
  torch.cuda.empty_cache()

  print('user_sentence:', user_sentence)
  print(f"예측된 감정 라벨: {predicted_class}")

  return predicted_class


test_sentence = "아무리그래도 이건 좀 아닌듯"
predict_user_sentence(test_sentence)



