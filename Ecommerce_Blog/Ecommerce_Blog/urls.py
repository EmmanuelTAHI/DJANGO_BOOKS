from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('e_commerce.urls')),  # Page d'accueil via l'app e_commerce
    path('blog/', include('blog.urls')),   # URLs pour l'app blog
    path('__reload__/', include('django_browser_reload.urls')),  # Pour le rechargement automatique
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Ajout des fichiers statiques et médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)