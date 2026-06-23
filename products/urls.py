from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('',                            views.category_list,   name='category_list'),
    path('men/',                        views.men_page,        name='men_page'),
    path('women/',                      views.women_page,      name='women_page'),
    path('search/',                     views.search,          name='search'),
    path('review/<int:product_id>/',    views.submit_review,   name='submit_review'),
    path('<slug:slug>/',                views.category_detail, name='category_detail'),
    path('item/<slug:slug>/',           views.product_detail,  name='product_detail'),
]
