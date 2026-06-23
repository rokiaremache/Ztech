# PATH: Ztech/core/views.py

from django.shortcuts import render
from products.models import Product, Category


def home(request):
    """
    Page d'accueil ZTech.
    Affiche 5 produits en vedette + catégories principales.
    """
    featured_products = Product.objects.filter(
        is_featured=True,
        is_active=True
    ).select_related('category', 'brand')[:5]

    new_products = Product.objects.filter(
        is_new=True,
        is_active=True
    ).select_related('category', 'brand')[:8]

    main_categories = Category.objects.filter(
        parent=None,
        is_active=True
    )

    context = {
        'featured_products': featured_products,
        'new_products':      new_products,
        'main_categories':   main_categories,
    }
    return render(request, 'pages/home.html', context)


def set_theme(request, theme):
    """
    Change le thème (men/women) et sauvegarde dans la session.
    Si l'utilisateur est connecté, sauvegarde dans son profil.
    """
    if theme in ('men', 'women'):
        request.session['theme'] = theme
        if request.user.is_authenticated:
            request.user.theme = theme
            request.user.save(update_fields=['theme'])

    # Redirige vers la page précédente
    next_url = request.GET.get('next', '/')
    from django.shortcuts import redirect
    return redirect(next_url)