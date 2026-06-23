def dashboard_context(request):
    if request.path.startswith('/dashboard/') and request.user.is_authenticated and request.user.is_staff:
        from orders.models import Order
        return {'pending_orders': Order.objects.filter(status='pending').count()}
    return {}
