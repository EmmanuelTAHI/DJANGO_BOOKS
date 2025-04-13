from .models import Panier, Wishlist

def counters(request):
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        panier, created = Panier.objects.get_or_create(user=request.user, defaults={'statut': 'en cours'})
        cart_count = panier.items.count()
    return {
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }