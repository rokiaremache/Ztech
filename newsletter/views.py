from django.shortcuts import redirect
from django.contrib import messages
from .models import Subscriber


def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            obj, created = Subscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Subscribed successfully!')
            else:
                messages.info(request, 'You are already subscribed.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
