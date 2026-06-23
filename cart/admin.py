# PATH: Ztech/cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model           = CartItem
    extra           = 0
    readonly_fields = ['unit_price', 'total_price', 'added_at']
    fields          = ['product', 'quantity', 'unit_price', 'total_price', 'added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display    = ['__str__', 'total_items', 'subtotal', 'total', 'qualifies_for_discount', 'updated_at']
    list_filter     = ['created_at']
    search_fields   = ['user__email', 'session_key']
    readonly_fields = ['total_items', 'subtotal', 'discount_amount', 'total', 'qualifies_for_discount']
    inlines         = [CartItemInline]