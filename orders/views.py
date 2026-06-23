# PATH: Ztech/orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import get_or_create_cart, create_order_from_cart
from accounts.forms import AddressForm
from .models import Order


def checkout(request):
    """
    Page de checkout — résumé du panier + formulaire adresse.
    Accessible sans être connecté.
    """
    cart = get_or_create_cart(request)

    if cart.total_items == 0:
        messages.error(request, 'Votre panier est vide.')
        return redirect('cart:cart_detail')

    # Pré-rempli si l'utilisateur a une adresse par défaut
    initial = {}
    if request.user.is_authenticated:
        default_address = request.user.get_default_address()
        if default_address:
            initial = {
                'full_name':   default_address.full_name,
                'phone':       default_address.phone,
                'street':      default_address.street,
                'city':        default_address.city,
                'wilaya':      default_address.wilaya,
                'postal_code': default_address.postal_code,
            }

    form = AddressForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        address_data = form.cleaned_data
        address_data['wilaya'] = dict(form.fields['wilaya'].choices).get(
            address_data['wilaya'], address_data['wilaya']
        )

        if request.user.is_authenticated:
            address_data['email'] = request.user.email
        else:
            address_data['email'] = request.POST.get('email', '')

        # Sauvegarde l'adresse dans la session pour le paiement
        request.session['checkout_address'] = {
            k: str(v) for k, v in address_data.items()
        }
        return redirect('payments:payment')

    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'pages/checkout.html', context)


def order_confirmation(request, reference):
    """
    Page de confirmation après paiement réussi.
    """
    order = get_object_or_404(Order, reference=reference)

    # Sécurité — seul le propriétaire peut voir sa commande
    if order.user and order.user != request.user:
        return redirect('core:home')

    return render(request, 'pages/order_confirmation.html', {'order': order})