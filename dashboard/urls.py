from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.orders_list, name='orders'),
    path('orders/<str:reference>/', views.order_detail, name='order_detail'),
    path('products/', views.products_list, name='products'),
    path('customers/', views.customers_list, name='customers'),
]
