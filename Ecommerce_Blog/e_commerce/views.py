from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .form import AuthForm
from .models import Livre, Wishlist, Panier, LignePanier, Categorie, LigneCommande, Commande
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json


# ==============================
# 🌐 Pages générales
# ==============================

def get_panier_user(request):
    if request.user.is_authenticated:
        panier, _ = Panier.objects.get_or_create(user=request.user, defaults={'statut': 'en cours'})
        return panier
    return None

def index(request):
    livres = Livre.objects.all()
    panier_user = get_panier_user(request)
    categories = Categorie.objects.all()
    return render(request, 'e_commerce/index.html', {
        'livres': livres,
        'panier_user': panier_user,
        'categories': categories
    })

def about(request):
    return render(request, 'e_commerce/about-us.html')

def contact(request):
    return render(request, 'e_commerce/contact-us.html')

def services(request):
    return render(request, 'e_commerce/services.html')

def my_profile(request):
    return render(request, 'e_commerce/my-profile.html')

# ==============================
# 🛒 Pages E-commerce / Boutique
# ==============================

@login_required
def shop_cart(request):
    panier, created = Panier.objects.get_or_create(user=request.user, defaults={'statut': 'en cours'})
    items = panier.items.select_related('livre')  # Récupère les lignes du panier
    total = sum(item.total() for item in items)

    # On convertit en int pour éviter les flottants
    total_int = int(total)
    frais_expedition = 1500  # Frais d'expédition fixes

    # Retourne les valeurs dans la réponse
    return render(request, 'e_commerce/shop-cart.html', {
        'items': items,
        'total': total_int,
        'frais_expedition': frais_expedition,
        'panier': panier
    })

@login_required
def add_to_cart(request, livre_id):
    if request.method == 'POST':
        livre = get_object_or_404(Livre, id=livre_id)
        panier, created = Panier.objects.get_or_create(user=request.user, defaults={'statut': 'en cours'})
        ligne, created = LignePanier.objects.get_or_create(panier=panier, livre=livre)
        if not created:
            ligne.quantite += 0
            ligne.save()
            return JsonResponse({'status': 'updated', 'message': f"Quantité de {livre.titre} augmentée dans le panier."})
        return JsonResponse({'status': 'added', 'message': f"{livre.titre} ajouté au panier."})
    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

@login_required
def remove_from_cart(request, livre_id):
    if request.method == 'POST':
        panier, created = Panier.objects.get_or_create(user=request.user, defaults={'statut': 'en cours'})
        try:
            item = LignePanier.objects.get(panier=panier, livre__id=livre_id)
            livre_titre = item.livre.titre  # Stocker le titre avant de supprimer
            item.delete()
            return JsonResponse({'status': 'removed', 'message': f"{livre_titre} retiré du panier.", 'livre_id': livre_id})
        except LignePanier.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': "Ce livre n'est pas dans votre panier."}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        livre_id = request.POST.get('livre_id')
        try:
            livre = Livre.objects.get(id=livre_id)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, livre=livre)
            if not created:
                wishlist_item.delete()
                return JsonResponse({'status': 'removed'})
            return JsonResponse({'status': 'added'})
        except Livre.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Livre non trouvé'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

@login_required
def remove_from_wishlist(request, livre_id):
    if request.method == 'POST':
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, livre_id=livre_id)
            wishlist_item.delete()
            return JsonResponse({'status': 'removed', 'livre_id': livre_id})
        except Wishlist.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': "Article introuvable"}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

@login_required
@csrf_exempt
def update_quantity(request):
    if request.method == 'POST':
        livre_id = request.POST.get('livre_id')
        quantite = int(request.POST.get('quantite'))

        panier = get_object_or_404(Panier, user=request.user)
        ligne = get_object_or_404(LignePanier, panier=panier, livre_id=livre_id)

        ligne.quantite = quantite
        ligne.save()

        return JsonResponse({'status': 'success', 'total_livre': ligne.total()})

    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

@login_required
def shop_checkout(request):
    panier, created = Panier.objects.get_or_create(user=request.user, defaults={'statut': 'en cours'})
    items = panier.items.select_related('livre')
    total = sum(item.total() for item in items)
    frais_expedition = 1500
    total_general = total + frais_expedition

    if not items:
        messages.error(request, "Votre panier est vide.")
        return redirect('e_commerce:index')

    if request.method == 'POST':
        country = request.POST.get('country')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        city = request.POST.get('city')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')
        card_holder = request.POST.get('card_holder')
        card_number = request.POST.get('card_number')
        card_expiry = request.POST.get('card_expiry')
        card_cvv = request.POST.get('card_cvv')
        operator = request.POST.get('operator')
        phone_number = request.POST.get('phone_number')

        errors = []
        if not country:
            errors.append("Veuillez sélectionner un pays.")
        if not first_name:
            errors.append("Veuillez entrer votre prénom.")
        if not last_name:
            errors.append("Veuillez entrer votre nom.")
        if not city:
            errors.append("Veuillez entrer une ville.")
        if not address:
            errors.append("Veuillez entrer une adresse.")
        if not email or '@' not in email:
            errors.append("Veuillez entrer un email valide.")
        if not phone:
            errors.append("Veuillez entrer un numéro de téléphone.")
        if not payment_method:
            errors.append("Veuillez sélectionner un mode de paiement.")
        if payment_method == 'credit-card':
            if not card_holder:
                errors.append("Veuillez entrer le nom du titulaire de la carte.")
            if not card_number or len(card_number.replace(' ', '')) < 16:
                errors.append("Veuillez entrer un numéro de carte valide.")
            if not card_expiry:
                errors.append("Veuillez entrer une date d'expiration.")
            if not card_cvv or len(card_cvv) < 3:
                errors.append("Veuillez entrer un CVV valide.")
        elif payment_method == 'mobile-money':
            if not operator:
                errors.append("Veuillez sélectionner un opérateur mobile.")
            if not phone_number:
                errors.append("Veuillez entrer un numéro pour le paiement mobile.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'e_commerce/shop-checkout.html', {
                'items': items,
                'total': total,
                'frais_expedition': frais_expedition,
                'total_general': total_general,
            })

        full_address = f"{first_name} {last_name}, {address}, {city}, {country}"
        order = Commande.objects.create(
            user=request.user,
            adresse_livraison=full_address,
            statut='en_attente',
        )

        for item in items:
            LigneCommande.objects.create(
                commande=order,
                livre=item.livre,
                quantite=item.quantite,
                prix_unitaire=item.livre.prix
            )

        context = {
            'order': order,
            'items': items,
            'total': total,
            'frais_expedition': frais_expedition,
            'total_general': total_general,
            'adresse_livraison': full_address,
            'email': email,
            'phone': phone,
            'payment_method': payment_method,
        }
        subject = 'Confirmation de votre commande'
        html_message = render_to_string('e_commerce/email_order_confirmation.html', context)
        plain_message = f"Votre commande a été confirmée. Total: {total_general} FCFA."

        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")

        items.delete()
        panier.statut = 'terminé'
        panier.save()

        messages.success(request, "Commande validée ! Un email de confirmation a été envoyé.")
        return redirect('e_commerce:index')

    return render(request, 'e_commerce/shop-checkout.html', {
        'items': items,
        'total': total,
        'frais_expedition': frais_expedition,
        'total_general': total_general,
    })

def shop_grid(request):
    livres = Livre.objects.all()
    return render(request, 'e_commerce/shop-grid.html', {'livres': livres})

def wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        context = {'wishlist_items': wishlist_items}
        return render(request, 'e_commerce/wishlist.html', context)
    else:
        return render(request, 'e_commerce/wishlist.html', {'wishlist_items': []})

# ==============================
# 📚 Pages Livres
# ==============================

def book_list(request):
    livres = Livre.objects.all()
    return render(request, 'e_commerce/books-list.html', {'livres': livres})

def book_detail(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    return render(request, 'e_commerce/books-detail.html', {'livre': livre})

def book_grid_view(request):
    livres = Livre.objects.all()
    return render(request, 'e_commerce/books-grid-view.html', {'livres': livres})

def book_grid_left_sidebar(request):
    livres = Livre.objects.all()
    return render(request, 'e_commerce/books-grid-left-sidebar.html', {'livres': livres})

def book_list_view_sidebar(request):
    livres = Livre.objects.all()
    return render(request, 'e_commerce/books-list-view-sidebar.html', {'livres': livres})

def book_grid_view_sidebar(request):
    livres = Livre.objects.all()
    paginator = Paginator(livres, 9)  # Pagination : 9 articles par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('livre_id', flat=True)
    return render(request, 'e_commerce/books-grid-view-sidebar.html', {'livres': page_obj, 'wishlist_ids': wishlist_ids})

# ==============================
# 🔐 Authentification
# ==============================

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 jours
            else:
                request.session.set_expiry(0)  # Session expire à la fermeture
            return redirect('e_commerce:index')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'registration/shop-login.html')

def deconnexion(request):
    logout(request)
    return redirect('e_commerce:index')

def inscription(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_superuser = True
            user.is_staff = True
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = get_current_site(request).domain
            activation_link = f"http://{domain}/activate/{uid}/{token}/"
            subject = "Activation de votre compte"
            message = f"""
            Bonjour {user.username},
            Merci de vous être inscrit. Veuillez cliquer sur le lien ci-dessous pour activer votre compte :
            {activation_link}
            Si vous n'avez pas demandé cette inscription, ignorez cet email.
            Merci,
            L'équipe de support.
            """
            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
            email.send(fail_silently=False)
            return redirect('e_commerce:login')
    else:
        form = AuthForm()
    return render(request, 'registration/shop-registration.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("e_commerce:index")
    return render(request, "registration/activation_failed.html")

# Suppression de process_order car on n'utilise plus AJAX
# @csrf_exempt
# def process_order(request):
#     ... (code supprimé car géré dans shop_checkout)