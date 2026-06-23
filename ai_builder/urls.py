from django.urls import path
from . import views

app_name = 'ai_builder'

urlpatterns = [
    path('', views.index, name='index'),
    path('suggest/', views.suggest_build, name='suggest'),
    path('calculate/', views.calculate_build, name='calculate'),
]
