# PATH: Ztech/accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import merge_guest_cart_on_login
from .models import CustomUser, Address
from .forms import LoginForm, RegisterForm, ProfileForm, AddressForm


def login_view(request):
    """
    Page de connexion.
    Après login, fusionne le panier guest avec le panier user.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email    = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user     = authenticate(request, username=email, password=password)

        if user:
            # Fusionne le panier guest avant le login
            merge_guest_cart_on_login(request, user)
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! 👋')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'pages/login.html', {'form': form})


def register_view(request):
    """Page d'inscription."""
    if request.user.is_authenticated:
        return redirect('core:home')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        merge_guest_cart_on_login(request, user)
        login(request, user)
        messages.success(request, f'Compte créé avec succès ! Bienvenue {user.first_name} 🎉')
        return redirect('core:home')

    return render(request, 'pages/register.html', {'form': form})


def logout_view(request):
    """Déconnexion."""
    logout(request)
    messages.success(request, 'Vous êtes déconnecté.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """Espace client — modifier les infos personnelles."""
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profil mis à jour avec succès !')
        return redirect('accounts:profile')

    return render(request, 'pages/profile.html', {'form': form})


@login_required
def address_list(request):
    """Liste des adresses du client."""
    addresses = request.user.addresses.all()
    return render(request, 'pages/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    """Ajouter une nouvelle adresse."""
    form = AddressForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, 'Adresse ajoutée avec succès !')
        return redirect('accounts:address_list')

    return render(request, 'pages/address_form.html', {'form': form, 'title': 'Ajouter une adresse'})


@login_required
def address_edit(request, pk):
    """Modifier une adresse existante."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=address)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Adresse modifiée avec succès !')
        return redirect('accounts:address_list')

    return render(request, 'pages/address_form.html', {'form': form, 'title': 'Modifier l\'adresse'})


@login_required
def address_delete(request, pk):
    """Supprimer une adresse."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Adresse supprimée.')
    return redirect('accounts:address_list')


@login_required
def address_set_default(request, pk):
    """Définir une adresse comme adresse par défaut."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'Adresse par défaut mise à jour.')
    return redirect('accounts:address_list')


@login_required
def order_history(request):
    """Historique des commandes du client."""
    orders = request.user.orders.prefetch_related('items').order_by('-created_at')
    return render(request, 'pages/order_history.html', {'orders': orders})


@login_required
def order_detail(request, reference):
    """Détail d'une commande spécifique."""
    from orders.models import Order
    order = get_object_or_404(Order, reference=reference, user=request.user)
    return render(request, 'pages/order_detail.html', {'order': order})