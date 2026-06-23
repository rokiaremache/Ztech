from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, ProductReview


def category_list(request):
    categories = Category.objects.filter(parent=None, is_active=True)
    return render(request, 'pages/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category    = get_object_or_404(Category, slug=slug, is_active=True)
    all_cats    = [category] + category.get_all_children()
    all_ids     = [c.id for c in all_cats]
    products    = Product.objects.filter(category__in=all_ids, is_active=True).select_related('category','brand')
    sort        = request.GET.get('sort', 'newest')
    if sort == 'price_asc':    products = products.order_by('price')
    elif sort == 'price_desc': products = products.order_by('-price')
    else:                      products = products.order_by('-created_at')
    return render(request, 'pages/category_detail.html', {
        'category': category, 'subcategories': category.children.filter(is_active=True),
        'products': products, 'sort': sort, 'total': products.count(),
    })


def product_detail(request, slug):
    product         = get_object_or_404(Product, slug=slug, is_active=True)
    similar         = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    gallery_images  = product.images.all()
    specs           = product.specs.all()
    reviews         = product.reviews.filter(is_approved=True).select_related('user')
    user_reviewed   = False
    if request.user.is_authenticated:
        user_reviewed = reviews.filter(user=request.user).exists()

    return render(request, 'pages/product_detail.html', {
        'product': product, 'similar_products': similar,
        'gallery_images': gallery_images, 'specs': specs,
        'reviews': reviews, 'user_reviewed': user_reviewed,
    })


@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if request.method != 'POST':
        return redirect('products:product_detail', slug=product.slug)

    # Check if user already reviewed
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('products:product_detail', slug=product.slug)

    rating = request.POST.get('rating')
    title  = request.POST.get('title', '').strip()
    body   = request.POST.get('body', '').strip()
    image  = request.FILES.get('image')

    if not rating or not body:
        messages.error(request, 'Rating and review text are required.')
        return redirect('products:product_detail', slug=product.slug)

    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        messages.error(request, 'Invalid rating.')
        return redirect('products:product_detail', slug=product.slug)

    ProductReview.objects.create(
        product = product,
        user    = request.user,
        rating  = rating,
        title   = title or f"{rating}-star review",
        body    = body,
        image   = image,
    )
    messages.success(request, 'Review submitted. Thank you!')
    return redirect('products:product_detail', slug=product.slug)


def men_page(request):
    categories = Category.objects.filter(gender__in=['men','all'], parent=None, is_active=True)
    featured   = Product.objects.filter(gender__in=['men','all'], is_active=True, is_featured=True)[:6]
    return render(request, 'men/home.html', {'categories': categories, 'featured': featured, 'theme': 'men'})


def women_page(request):
    categories = Category.objects.filter(gender__in=['women','all'], parent=None, is_active=True)
    featured   = Product.objects.filter(gender__in=['women','all'], is_active=True, is_featured=True)[:6]
    return render(request, 'women/home.html', {'categories': categories, 'featured': featured, 'theme': 'women'})


def search(request):
    query    = request.GET.get('q', '')
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(is_active=True).filter(
            Q(name__icontains=query) | Q(short_description__icontains=query)
        ).select_related('category','brand')
    return render(request, 'pages/search.html', {'query': query, 'products': products, 'total': products.count()})
