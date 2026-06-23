# PATH: Ztech/accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',                          views.login_view,           name='login'),
    path('logout/',                         views.logout_view,          name='logout'),
    path('register/',                       views.register_view,        name='register'),
    path('profile/',                        views.profile_view,         name='profile'),
    path('addresses/',                      views.address_list,         name='address_list'),
    path('addresses/add/',                  views.address_add,          name='address_add'),
    path('addresses/<int:pk>/edit/',        views.address_edit,         name='address_edit'),
    path('addresses/<int:pk>/delete/',      views.address_delete,       name='address_delete'),
    path('addresses/<int:pk>/default/',     views.address_set_default,  name='address_set_default'),
    path('orders/',                         views.order_history,        name='order_history'),
    path('orders/<str:reference>/',         views.order_detail,         name='order_detail'),
]