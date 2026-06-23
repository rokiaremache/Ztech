import re
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from core.utils import (
    get_or_create_cart, create_order_from_cart,
    reduce_stock, send_order_confirmation_email
)
from orders.models import Order


# ── Validation helpers ───────────────────────────────────────────

def _validate_card(card_number, card_name, card_expiry, card_cvv):
    """
    Returns list of error strings. Empty list = all valid.
    """
    errors = []

    # Card number — exactly 16 digits
    digits = card_number.replace(' ', '').replace('-', '')
    if not digits.isdigit():
        errors.append('Card number must contain digits only.')
    elif len(digits) != 16:
        errors.append(f'Card number must be exactly 16 digits (you entered {len(digits)}).')

    # Card name
    if not card_name or len(card_name.strip()) < 2:
        errors.append('Cardholder name is required.')

    # Expiry — MM/YY, must not be in the past
    if not re.match(r'^\d{2}/\d{2}$', card_expiry):
        errors.append('Expiry date must be in MM/YY format.')
    else:
        try:
            month = int(card_expiry[:2])
            year  = int(card_expiry[3:]) + 2000
            if month < 1 or month > 12:
                errors.append('Invalid expiry month.')
            else:
                now = datetime.now()
                # Card expires at the END of the stated month
                if (year, month) < (now.year, now.month):
                    errors.append('Your card is expired.')
        except ValueError:
            errors.append('Invalid expiry date.')

    # CVV — exactly 3 digits
    if not re.match(r'^\d{3}$', card_cvv):
        errors.append('CVV must be exactly 3 digits.')

    # Simulate a declined card (test mode — starts with 0000)
    if digits.startswith('0000'):
        errors.append('Payment declined by your bank. Please use a different card.')

    return errors


# ── Views ────────────────────────────────────────────────────────

def payment_page(request):
    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        return redirect('cart:cart_detail')

    address_data = request.session.get('checkout_address')
    if not address_data:
        return redirect('orders:checkout')

    return render(request, 'pages/payment.html', {
        'cart': cart,
        'address': address_data,
        'errors': request.session.pop('payment_errors', []),
    })


def process_payment(request):
    if request.method != 'POST':
        return redirect('payments:payment')

    cart         = get_or_create_cart(request)
    address_data = request.session.get('checkout_address')

    if not cart or cart.total_items == 0 or not address_data:
        messages.error(request, 'Your session expired. Please start your order again.')
        return redirect('cart:cart_detail')

    card_number = request.POST.get('card_number', '')
    card_name   = request.POST.get('card_name', '').strip()
    card_expiry = request.POST.get('card_expiry', '').strip()
    card_cvv    = request.POST.get('card_cvv', '').strip()

    # Strict validation — if ANY error, no order created
    errors = _validate_card(card_number, card_name, card_expiry, card_cvv)

    if errors:
        request.session['payment_errors'] = errors
        return redirect('payments:payment')

    # All good — create order, mark paid, send email
    user  = request.user if request.user.is_authenticated else None
    order = create_order_from_cart(cart, address_data, user)
    order.status  = 'paid'
    order.paid_at = timezone.now()
    order.save(update_fields=['status', 'paid_at'])

    reduce_stock(order.items.all())

    # Clear cart + session
    cart.items.all().delete()
    cart.delete()
    request.session.pop('checkout_address', None)

    send_order_confirmation_email(order)

    return redirect('orders:order_confirmation', reference=order.reference)


def payment_failed(request):
    """Explicit failure page."""
    return render(request, 'pages/payment_failed.html')
