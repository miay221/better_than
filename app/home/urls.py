# home 의 urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home_index'),
    path('qr/', views.qr, name='home_qr'),
    path('save_feedback/', views.save_feedback, name='save_feedback'),
]
