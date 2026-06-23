from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductSpec, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display   = ['name', 'parent', 'gender', 'product_count', 'thumbnail', 'is_active']
    list_filter    = ['gender', 'parent', 'is_active']
    search_fields  = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable  = ['is_active']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:4px;">', obj.image.url)
        return '—'
    thumbnail.short_description = 'Image'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display  = ['name', 'logo_preview', 'website', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width:40px;height:40px;object-fit:contain;">', obj.logo.url)
        return '—'
    logo_preview.short_description = 'Logo'


class ProductImageInline(admin.TabularInline):
    model  = ProductImage
    extra  = 2
    fields = ['image', 'alt_text', 'order']


class ProductSpecInline(admin.TabularInline):
    model  = ProductSpec
    extra  = 3
    fields = ['key', 'value', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ['thumbnail', 'name', 'component_type', 'category', 'brand', 'price', 'stock', 'is_featured', 'is_active']
    list_filter    = ['is_active', 'is_featured', 'component_type', 'gender', 'category']
    search_fields  = ['name', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    list_editable  = ['is_featured', 'is_active', 'stock']
    inlines        = [ProductImageInline, ProductSpecInline]
    fieldsets = (
        ('Core Info', {'fields': ('name', 'slug', 'sku', 'category', 'brand', 'gender')}),
        ('Builder Info', {'fields': ('component_type', 'socket', 'ram_type', 'wattage'), 'description': 'Required for AI Builder and Compatibility Calculator'}),
        ('Pricing', {'fields': ('price', 'old_price', 'discount_percent')}),
        ('Content', {'fields': ('short_description', 'description', 'main_image')}),
        ('Inventory & Flags', {'fields': ('stock', 'is_active', 'is_featured', 'is_new')}),
    )

    def thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="width:44px;height:44px;object-fit:cover;border-radius:4px;">', obj.main_image.url)
        return '—'
    thumbnail.short_description = ''


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display  = ['product', 'user', 'rating', 'title', 'review_image', 'is_approved', 'created_at']
    list_filter   = ['rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'user__email', 'title']
    readonly_fields = ['product', 'user', 'rating', 'title', 'body', 'image', 'created_at']

    def review_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:44px;height:44px;object-fit:cover;border-radius:4px;">', obj.image.url)
        return '—'
    review_image.short_description = 'Photo'
