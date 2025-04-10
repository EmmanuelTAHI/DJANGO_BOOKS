from django.urls import path
from . import views

app_name = 'blog'  # Namespace pour éviter les conflits avec d'autres apps

urlpatterns = [
    path('', views.article_list, name='article_list'),          # Liste des articles (ex. /blog/)
    path('<slug:slug>/', views.article_detail, name='article_detail'),  # Détail d’un article (ex. /blog/mon-article-2025/)
]