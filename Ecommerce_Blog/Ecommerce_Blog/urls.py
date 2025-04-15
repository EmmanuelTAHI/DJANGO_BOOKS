from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuration de la documentation de l'API
schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce Blog API",
        default_version='v1',
        description="Documentation de l'API pour Ecommerce et Blog",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@monsite.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]

)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('e_commerce.urls')),  # Page d'accueil via l'app e_commerce
    path('blog/', include('blog.urls')),  # URLs pour l'app blog
    path('__reload__/', include('django_browser_reload.urls')),  # Pour le rechargement automatique
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # API routes pour chaque application directement
    path('api/e_commerce/', include('e_commerce.urls')),  # Routes API pour l'app e_commerce
    path('api/blog/', include('blog.urls')),  # Routes API pour l'app blog

    # Ajoute ces deux routes :
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Documentation de l'API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-schema'),
]

# Ajout des fichiers statiques et médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
