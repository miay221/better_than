from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chatbot_index'),
    path('analyze_message/', views.analyze_message, name='analyze_message'),
]
