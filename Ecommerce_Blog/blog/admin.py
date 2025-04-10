from django.contrib import admin
from .models import Categorie, Tag, Article, Commentaire

# Enregistrement de Categorie
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'statut', 'created_at', 'last_updated_at')
    list_filter = ('statut', 'created_at')
    search_fields = ('nom',)

# Enregistrement de Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nom', 'statut', 'created_at', 'last_updated_at')
    list_filter = ('statut', 'created_at')
    search_fields = ('nom',)

# Enregistrement de Article
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur_id', 'categorie_id', 'date_de_publication', 'est_publie', 'statut', 'created_at')
    list_filter = ('statut', 'date_de_publication', 'categorie_id')
    search_fields = ('titre', 'resume', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}  # Auto-remplit le slug à partir du titre
    raw_id_fields = ('auteur_id', 'livre_associe_id')  # Pour faciliter la sélection si beaucoup d'utilisateurs/livres
    filter_horizontal = ('tag_ids',)  # Interface conviviale pour les tags

# Enregistrement de Commentaire
@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('article', 'auteur_id', 'contenu_short', 'parent_id', 'statut', 'created_at')
    list_filter = ('statut', 'created_at', 'article')
    search_fields = ('contenu', 'auteur_id__username')
    raw_id_fields = ('auteur_id', 'article', 'parent_id')  # Pour éviter les listes déroulantes lourdes

    def contenu_short(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu
    contenu_short.short_description = 'Contenu (extrait)'