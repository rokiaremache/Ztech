"""
ZTech — Core business logic utilities.
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
import logging

logger = logging.getLogger(__name__)


# ── CART ────────────────────────────────────────────────────────

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key, user=None
        )
    return cart


def merge_guest_cart_on_login(request, user):
    if not request.session.session_key:
        return
    try:
        guest_cart = Cart.objects.get(session_key=request.session.session_key, user=None)
        user_cart, _ = Cart.objects.get_or_create(user=user)
        user_cart.merge_with(guest_cart)
    except Cart.DoesNotExist:
        pass


def check_stock_availability(product, quantity):
    if product.stock >= quantity:
        return {'available': True}
    return {'available': False, 'message': f'Only {product.stock} unit(s) available.'}


def reduce_stock(order_items):
    from django.db.models import F
    for item in order_items:
        if item.product:
            item.product.__class__.objects.filter(pk=item.product.pk).update(
                stock=F('stock') - item.quantity
            )


# ── DISCOUNT ─────────────────────────────────────────────────────

def calculate_discount(subtotal):
    threshold = getattr(settings, 'CART_DISCOUNT_THRESHOLD', 500000)
    rate      = getattr(settings, 'CART_DISCOUNT_RATE', 0.10)
    if float(subtotal) >= threshold:
        discount = float(subtotal) * rate
        return {
            'subtotal':        float(subtotal),
            'discount_amount': discount,
            'total':           float(subtotal) - discount,
            'qualifies':       True,
            'missing':         0,
        }
    return {
        'subtotal':        float(subtotal),
        'discount_amount': 0,
        'total':           float(subtotal),
        'qualifies':       False,
        'missing':         threshold - float(subtotal),
    }


# ── ORDER CREATION ───────────────────────────────────────────────

def create_order_from_cart(cart, address_data, user=None):
    subtotal = float(cart.subtotal)
    disc     = calculate_discount(subtotal)

    order = Order.objects.create(
        user             = user,
        full_name        = address_data.get('full_name', ''),
        email            = address_data.get('email', getattr(user, 'email', '') if user else ''),
        phone            = address_data.get('phone', ''),
        street           = address_data.get('street', ''),
        city             = address_data.get('city', ''),
        wilaya           = address_data.get('wilaya', ''),
        postal_code      = address_data.get('postal_code', ''),
        customer_notes   = address_data.get('customer_notes', ''),
        subtotal         = subtotal,
        discount_amount  = disc['discount_amount'],
        total            = disc['total'],
    )

    for item in cart.items.select_related('product').all():
        OrderItem.objects.create(
            order         = order,
            product       = item.product,
            product_name  = item.product.name,
            product_image = str(item.product.main_image) if item.product.main_image else '',
            unit_price    = item.product.price,
            quantity      = item.quantity,
        )

    return order


# ── EMAIL ────────────────────────────────────────────────────────

def _send_email(subject, plain_body, html_body, recipient):
    """Low-level helper — sends and logs result."""
    try:
        msg = EmailMultiAlternatives(
            subject    = subject,
            body       = plain_body,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [recipient],
        )
        if html_body:
            msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        logger.info("Email sent: %s → %s", subject, recipient)
        return True
    except Exception as e:
        logger.warning("Email not sent (%s → %s): %s", subject, recipient, e)
        return False


def send_order_confirmation_email(order):
    """Send rich HTML confirmation email after successful payment."""
    if not order.email:
        return False

    context = {
        'order':       order,
        'order_items': order.items.select_related('product').all(),
        'site_name':   'ZTech',
        'site_url':    getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
    }

    try:
        html  = render_to_string('emails/order_confirmation.html', context)
        plain = render_to_string('emails/order_confirmation.txt',  context)
    except Exception as e:
        logger.error("Email template error: %s", e)
        plain = f"Thank you {order.full_name}! Order {order.reference} confirmed. Total: {order.total:,.0f} DZD."
        html  = None

    return _send_email(
        subject    = f"ZTech — Order Confirmed #{order.reference}",
        plain_body = plain,
        html_body  = html,
        recipient  = order.email,
    )


def send_order_cancellation_email(order, reason, was_paid=None):
    """Send cancellation email when admin cancels an order."""
    if not order.email:
        return False

    # was_paid may be passed explicitly (before status was changed to 'cancelled')
    # Fall back to order.is_paid for backwards-compatibility.
    if was_paid is None:
        was_paid = order.is_paid

    context = {
        'order':    order,
        'reason':   reason,
        'was_paid': was_paid,
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
    }

    try:
        html  = render_to_string('emails/order_cancelled.html', context)
        plain = render_to_string('emails/order_cancelled.txt',  context)
    except Exception as e:
        logger.error("Cancellation email template error: %s", e)
        plain = (
            f"Dear {order.full_name},\n\n"
            f"Your order #{order.reference} has been cancelled.\n"
            f"Reason: {reason}\n\n"
            f"If you paid, a refund will be processed within 3–5 business days.\n\n"
            f"— ZTech Team"
        )
        html = None

    return _send_email(
        subject    = f"Order Cancelled — #{order.reference} — ZTech",
        plain_body = plain,
        html_body  = html,
        recipient  = order.email,
    )