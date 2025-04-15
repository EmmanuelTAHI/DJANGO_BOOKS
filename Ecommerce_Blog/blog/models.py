from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField


class Categorie(models.Model):
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    nom = models.CharField(max_length=100, unique=True)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


class Tag(models.Model):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    nom = models.CharField(max_length=100, unique=True)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


class Article(models.Model):
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    titre = models.CharField(max_length=255)
    couverture = models.ImageField(upload_to="articles/")
    resume = models.TextField(blank=True)
    contenu = RichTextField()

    auteur_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="auteur_article_ids")
    categorie_id = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True,
                                     related_name="categorie_article_ids", verbose_name="Catégorie")
    tag_ids = models.ManyToManyField(Tag, blank=True, related_name="tag_article_ids", verbose_name="Tags")

    est_publie = models.BooleanField(default=False)
    livre_associe_id = models.ForeignKey('e_commerce.Livre', on_delete=models.SET_NULL, null=True, blank=True)
    date_de_publication = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(default="", unique=True, blank=True)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre) + "-" + str(self.date_de_publication.year)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre


class Commentaire(models.Model):
    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    auteur_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="auteur_commentaire_ids")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="article_commentaire_ids")
    contenu = models.TextField(max_length=1000)

    # Standards
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.article.titre}"