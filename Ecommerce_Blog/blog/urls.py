from django.urls import path
from . import views

app_name = 'blog'  # Namespace pour éviter les conflits avec d'autres apps

urlpatterns = [
    path('', views.blog_grid_left_sidebar, name='blog-grid-left-sidebar'),          # Liste des articles (ex. /blog/)
    path('blog-grid-no-sidebar/', views.blog_grid_no_sidebar, name='blog-grid-no-sidebar'),
    path('blog-detail', views.blog_detail, name='blog-detail'),
    #path('<slug:slug>/', views.blog_detail, name='blog-detail'),  # Détail d’un article (ex. /blog/mon-article-2025/)
]