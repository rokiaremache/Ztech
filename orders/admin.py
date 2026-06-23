# PATH: Ztech/orders/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ['product_name', 'unit_price', 'quantity', 'total_price']
    fields          = ['product', 'product_name', 'unit_price', 'quantity', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = [
        'reference', 'full_name', 'email',
        'subtotal', 'discount_amount', 'total',
        'status_badge', 'created_at'
    ]
    list_filter     = ['status', 'created_at', 'wilaya']
    search_fields   = ['reference', 'email', 'full_name', 'phone']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at']
    inlines         = [OrderItemInline]
    actions         = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    fieldsets = (
        ('📋 Order Info',       {'fields': ('reference', 'user', 'status')}),
        ('📦 Delivery Address', {'fields': ('full_name', 'email', 'phone', 'street', 'city', 'wilaya', 'postal_code')}),
        ('💰 Pricing',          {'fields': ('subtotal', 'discount_amount', 'total')}),
        ('📝 Notes',            {'fields': ('customer_notes', 'admin_notes')}),
        ('📅 Timestamps',       {'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'), 'classes': ('collapse',)}),
    )

    def status_badge(self, obj):
        colors = {
            'pending':      '#f59e0b',
            'paid':         '#10b981',
            'processing':   '#3b82f6',
            'shipped':      '#6366f1',
            'delivered':    '#10b981',
            'cancelled':    '#6b7280',
            'refunded':     '#6b7280',
            'failed':       '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid', paid_at=timezone.now())
        self.message_user(request, f"{queryset.count()} order(s) marked as paid.")
    mark_as_paid.short_description = "✅ Mark as Paid"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f"{queryset.count()} order(s) marked as shipped.")
    mark_as_shipped.short_description = "🚚 Mark as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f"{queryset.count()} order(s) marked as delivered.")
    mark_as_delivered.short_description = "🏠 Mark as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} order(s) cancelled.")
    mark_as_cancelled.short_description = "❌ Cancel Orders"