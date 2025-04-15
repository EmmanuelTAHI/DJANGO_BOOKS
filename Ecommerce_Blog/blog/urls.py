from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .viewsets import BlogCategorieViewSet, BlogTagViewSet, ArticleViewSet, CommentaireViewSet

# Initialisation du routeur
router = DefaultRouter()
router.register(r'categories', BlogCategorieViewSet)
router.register(r'tags', BlogTagViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'commentaires', CommentaireViewSet)

app_name = 'blog'  # Namespace pour éviter les conflits avec d'autres apps

urlpatterns = [
    path('', views.blog_grid_no_sidebar, name='blog-grid-no-sidebar'),          # Liste des articles (ex. /blog/)
    path('blog-grid-left-sidebar/', views.blog_grid_left_sidebar, name='blog-grid-left-sidebar'),
    path('<slug:slug>/', views.blog_detail, name='blog-detail'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]