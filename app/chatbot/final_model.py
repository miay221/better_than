import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from konlpy.tag import Komoran
import asyncio
from lime.lime_text import LimeTextExplainer

# Komoran 형태소 분석기 초기화
komoran = Komoran()

# Hugging Face에서 모델과 토크나이저 로드
MODEL_PATH = "miayyyyy/kcBERT_downstream_model"  # Hugging Face 업로드된 모델 경로
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# 전처리 함수 정의
def extract_lemma(text):
    """Komoran으로 형태소 추출"""
    morphs = komoran.morphs(text)
    return " ".join(morphs)

def preprocess_text(text):
    """사용자 텍스트 전처리"""
    text = re.sub(r'[\U0001F600-\U0001F64F]', '😊', text)  # 기본 이모티콘을 웃는 이모티콘으로 대체
    text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # 기타 심볼 이모티콘 제거
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # 운송 이모티콘 제거
    text = re.sub(r'\s+', ' ', text).strip()             # 과도한 공백 제거
    text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s]', '', text)  # 한글, 영어, 숫자, 공백 이외 제거
    text = extract_lemma(text)  # 형태소 추출
    return text

# 감정 예측 함수 정의
async def predict_emotion_async(text):
    """사용자 텍스트를 입력받아 감정 라벨 예측"""
    # 텍스트 전처리
    processed_text = preprocess_text(text)

    # 토크나이징
    inputs = tokenizer(processed_text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)

    await asyncio.sleep(0) # 비동기 작업 예약

    # 모델 추론
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        predicted_class = torch.argmax(probabilities).item()  # 가장 높은 확률의 클래스 반환

    return {
        "processed_text": processed_text,
        "predicted_class": predicted_class,
        "probabilities": probabilities.tolist()  # 각 클래스별 확률 반환
    }


async def generate_lime_explanation(text):
    explainer = LimeTextExplainer(class_names=["매우 좋지 않음", "좋지 않음", "보통", "좋음", "매우 좋음"])

    def predict_proba(texts):
        inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=150)
        with torch.no_grad():
            logits = model(**inputs).logits
            proba = torch.softmax(logits, dim=-1).cpu().numpy()
        return proba
    
    processed_text = preprocess_text(text)

    explanation = await asyncio.to_thread(
        explainer.explain_instance,
        processed_text,
        predict_proba,
        num_features=8
    )

    lime_html = explanation.as_html()
    return lime_html