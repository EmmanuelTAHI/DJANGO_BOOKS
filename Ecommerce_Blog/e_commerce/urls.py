from django.urls import path
from . import views
from .views import activate_account, book_detail

app_name = 'e_commerce'

urlpatterns = [
    # Pages générales
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('my-profile/', views.my_profile, name='my-profile'),

    # E-commerce / Boutique
    path('wishlist/', views.wishlist, name='wishlist'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle-wishlist'),
    path('remove-from-wishlist/<int:livre_id>/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('remove-from-cart/<int:livre_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('add-to-cart/<int:livre_id>/', views.add_to_cart, name='add-to-cart'),
    path('shop-grid/', views.shop_grid, name='shop-grid'),
    path('shop-cart/', views.shop_cart, name='shop-cart'),
    path('shop-checkout/', views.shop_checkout, name='shop-checkout'),

    # Livres
    path('book-list/', views.book_list, name='book-list'),
    path('book-detail/<int:livre_id>/', book_detail, name='book-detail'),
    path('book-grid-view/', views.book_grid_view, name='book-grid-view'),
    path('book-grid-left-sidebar/', views.book_grid_left_sidebar, name='book-grid-left-sidebar'),
    path('book-grid-no-sidebar/', views.book_grid_no_sidebar, name='book-grid-no-sidebar'),
    path('book-list-view-sidebar/', views.book_list_view_sidebar, name='book-list-view-sidebar'),
    path('book-grid-view-sidebar/', views.book_grid_view_sidebar, name='book-grid-view-sidebar'),

    # Authentification
    path('login/', views.connexion, name='login'),
    path('register/', views.inscription, name='register'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate-account'),
]