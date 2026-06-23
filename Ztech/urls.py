from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header  = "ZTech Administration"
admin.site.site_title   = "ZTech Admin"
admin.site.index_title  = "Welcome to ZTech Admin Panel"

urlpatterns = [
    path('admin/',       admin.site.urls),
    path('',             include('core.urls')),
    path('products/',    include('products.urls')),
    path('accounts/',    include('accounts.urls')),
    path('cart/',        include('cart.urls')),
    path('orders/',      include('orders.urls')),
    path('payments/',    include('payments.urls')),
    path('ai-builder/',  include('ai_builder.urls')),
    path('gallery/',     include('gallery.urls')),
    path('newsletter/',  include('newsletter.urls')),
    path('api/',         include('api.urls')),
    path('dashboard/',   include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
