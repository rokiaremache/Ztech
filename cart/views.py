# PATH: Ztech/cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from core.utils import get_or_create_cart, check_stock_availability
from .models import Cart, CartItem


def cart_detail(request):
    """
    Page du panier — affiche tous les produits + total + discount.
    """
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()

    context = {
        'cart':     cart,
        'items':    items,
    }
    return render(request, 'pages/cart.html', context)


def add_to_cart(request, product_id):
    """
    Ajoute un produit au panier.
    Fonctionne pour guest et utilisateur connecté.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    # Vérifie le stock
    stock_check = check_stock_availability(product, quantity)
    if not stock_check['available']:
        messages.error(request, stock_check['message'])
        return redirect('products:product_detail', slug=product.slug)

    cart = get_or_create_cart(request)

    # Si le produit est déjà dans le panier, augmente la quantité
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = item.quantity + quantity
        stock_check2 = check_stock_availability(product, new_quantity)
        if not stock_check2['available']:
            messages.error(request, stock_check2['message'])
        else:
            item.quantity = new_quantity
            item.save()
            messages.success(request, f'"{product.name}" mis à jour dans le panier.')
    else:
        messages.success(request, f'"{product.name}" ajouté au panier !')

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success':      True,
            'cart_count':   cart.total_items,
            'cart_total':   float(cart.total),
        })

    return redirect('cart:cart_detail')


def remove_from_cart(request, item_id):
    """
    Supprime un article du panier.
    """
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = item.product.name
    item.delete()
    messages.success(request, f'"{product_name}" retiré du panier.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success':      True,
            'cart_count':   cart.total_items,
            'cart_total':   float(cart.total),
        })

    return redirect('cart:cart_detail')


def update_cart(request, item_id):
    """
    Met à jour la quantité d'un article dans le panier.
    """
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        item.delete()
        messages.success(request, 'Article retiré du panier.')
    else:
        stock_check = check_stock_availability(item.product, quantity)
        if not stock_check['available']:
            messages.error(request, stock_check['message'])
        else:
            item.quantity = quantity
            item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success':      True,
            'cart_count':   cart.total_items,
            'cart_total':   float(cart.total),
            'item_total':   float(item.total_price) if item.pk else 0,
        })

    return redirect('cart:cart_detail')


def clear_cart(request):
    """Vide complètement le panier."""
    cart = get_or_create_cart(request)
    cart.clear()
    messages.success(request, 'Panier vidé.')
    return redirect('cart:cart_detail')