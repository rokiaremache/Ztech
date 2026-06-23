# PATH: Ztech/core/context_processors.py

def cart_context(request):
    """Inject cart item count and total into every template."""
    from cart.models import Cart

    cart_items = 0
    cart_total = 0

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None

        if cart:
            cart_items = cart.total_items
            cart_total = cart.total
    except Exception:
        pass

    return {
        'cart_item_count': cart_items,
        'cart_total':      cart_total,
    }


def theme_context(request):
    """Inject current theme into every template."""
    theme = 'men'  # default

    if request.user.is_authenticated:
        theme = getattr(request.user, 'theme', 'men')
    elif 'theme' in request.session:
        theme = request.session['theme']

    return {
        'current_theme': theme,
        'is_dark_theme': theme == 'men',
        'is_cute_theme': theme == 'women',
    }