from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('',        views.payment_page,    name='payment'),
    path('process/', views.process_payment, name='process'),
    path('failed/',  views.payment_failed,  name='failed'),
]
