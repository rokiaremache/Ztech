from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product, Category
from accounts.models import CustomUser
from newsletter.models import Subscriber
from core.utils import send_order_cancellation_email


@staff_member_required(login_url='/accounts/login/')
def dashboard_home(request):
    now         = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_revenue   = Order.objects.filter(status__in=['paid','shipped','delivered']).aggregate(t=Sum('total'))['t'] or 0
    month_revenue   = Order.objects.filter(status__in=['paid','shipped','delivered'], created_at__gte=month_start).aggregate(t=Sum('total'))['t'] or 0
    total_orders    = Order.objects.count()
    pending_orders  = Order.objects.filter(status='pending').count()
    total_customers = CustomUser.objects.filter(is_staff=False).count()
    total_products  = Product.objects.filter(is_active=True).count()
    low_stock       = Product.objects.filter(stock__gt=0, stock__lte=3).count()
    out_of_stock    = Product.objects.filter(stock=0).count()
    recent_orders   = Order.objects.select_related('user').order_by('-created_at')[:8]

    daily_revenue = []
    for i in range(6, -1, -1):
        day       = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end   = day_start + timedelta(days=1)
        rev = Order.objects.filter(
            status__in=['paid','shipped','delivered'],
            created_at__gte=day_start, created_at__lt=day_end
        ).aggregate(t=Sum('total'))['t'] or 0
        daily_revenue.append({'day': day.strftime('%a'), 'revenue': float(rev)})

    return render(request, 'dashboard/home.html', {
        'total_revenue': total_revenue, 'month_revenue': month_revenue,
        'total_orders': total_orders,   'pending_orders': pending_orders,
        'total_customers': total_customers, 'total_products': total_products,
        'low_stock': low_stock, 'out_of_stock': out_of_stock,
        'recent_orders': recent_orders, 'daily_revenue': daily_revenue,
    })


@staff_member_required(login_url='/accounts/login/')
def orders_list(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related('items')
    if status_filter:
        orders = orders.filter(status=status_filter)
    orders = orders.order_by('-created_at')
    counts = {s[0]: Order.objects.filter(status=s[0]).count() for s in Order.STATUS_CHOICES}
    return render(request, 'dashboard/orders.html', {
        'orders': orders, 'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES, 'counts': counts,
    })


@staff_member_required(login_url='/accounts/login/')
def order_detail(request, reference):
    order = get_object_or_404(Order, reference=reference)

    if request.method == 'POST':
        action = request.POST.get('action', 'update_status')

        # ── Cancel with reason ──────────────────────────────────
        if action == 'cancel':
            reason = request.POST.get('cancellation_reason', '').strip()
            if not reason:
                messages.error(request, 'A cancellation reason is required.')
            elif not order.can_be_cancelled:
                messages.error(request, f'Order in status "{order.get_status_display()}" cannot be cancelled.')
            else:
                was_paid = order.is_paid  # capture before status changes
                order.status               = 'cancelled'
                order.cancellation_reason  = reason
                order.cancelled_at         = timezone.now()
                order.admin_notes          = request.POST.get('admin_notes', order.admin_notes)
                order.save(update_fields=['status', 'cancellation_reason', 'cancelled_at', 'admin_notes'])

                # Send cancellation email
                sent = send_order_cancellation_email(order, reason, was_paid=was_paid)
                msg = f'Order {reference} cancelled.'
                if sent:
                    msg += ' Cancellation email sent to customer.'
                else:
                    msg += ' (Email could not be sent — check SMTP config.)'
                messages.success(request, msg)
                return redirect('dashboard:order_detail', reference=reference)

        # ── Normal status update ────────────────────────────────
        else:
            new_status = request.POST.get('status')
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                if new_status == 'paid'      and not order.paid_at:      order.paid_at      = timezone.now()
                if new_status == 'shipped'   and not order.shipped_at:   order.shipped_at   = timezone.now()
                if new_status == 'delivered' and not order.delivered_at: order.delivered_at = timezone.now()
                order.admin_notes = request.POST.get('admin_notes', order.admin_notes)
                order.save()
                messages.success(request, f'Order {reference} updated to {order.get_status_display()}.')
                return redirect('dashboard:order_detail', reference=reference)

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required(login_url='/accounts/login/')
def products_list(request):
    products = Product.objects.select_related('category', 'brand').order_by('-created_at')
    search   = request.GET.get('q', '')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    return render(request, 'dashboard/products.html', {'products': products, 'search': search})


@staff_member_required(login_url='/accounts/login/')
def customers_list(request):
    customers = CustomUser.objects.filter(is_staff=False).annotate(
        order_count=Count('orders')
    ).order_by('-date_joined')
    return render(request, 'dashboard/customers.html', {'customers': customers})