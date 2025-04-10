from django.db import models
from django.contrib.auth.models import User
import random
import string


class Categorie(models.Model):
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    nom = models.CharField(verbose_name="Nom", max_length=100, unique=True)
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


class Tag(models.Model):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    nom = models.CharField(verbose_name="Nom", max_length=100, unique=True)
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


class Livre(models.Model):
    FORMAT_CHOICES = [
        ('Paperback', 'Paperback'),
        ('Hardcover', 'Hardcover'),
        ('Ebook', 'Ebook'),
        ('Audiobook', 'Audiobook'),
    ]

    LANGUE_CHOICES = [
        ('FR', 'Français'),
        ('EN', 'English'),
        ('ES', 'Español'),
        ('DE', 'Deutsch'),
    ]

    titre = models.CharField(max_length=255)
    couverture = models.ImageField(upload_to='couvertures/')
    auteur = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    langue = models.CharField(max_length=2, choices=LANGUE_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    date_publication = models.DateField(blank=True, null=True)
    editeur = models.CharField(max_length=255,blank=True, null=True)
    nombre_pages = models.PositiveIntegerField(blank=True, null=True)
    nombre_chapitres = models.PositiveIntegerField(blank=True, null=True)
    nombre_topics = models.PositiveIntegerField(blank=True, null=True)

    prix = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)

    categorie_ids = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='livres')
    tags_ids = models.ManyToManyField(Tag, blank=True)

    description = models.TextField(blank=True)

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def generate_isbn(self):
        """Génère un ISBN-13 fictif aléatoire."""
        prefix = "978"
        body = ''.join(random.choices(string.digits, k=9))
        isbn = prefix + body
        check_digit = self.calculate_check_digit(isbn)
        return isbn + str(check_digit)

    def calculate_check_digit(self, isbn):
        total = 0
        for i, digit in enumerate(isbn):
            digit = int(digit)
            total += digit if i % 2 == 0 else digit * 3
        check_digit = (10 - (total % 10)) % 10
        return check_digit

    def save(self, *args, **kwargs):
        if not self.isbn:
            while True:
                new_isbn = self.generate_isbn()
                if not Livre.objects.filter(isbn=new_isbn).exists():
                    self.isbn = new_isbn
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'livre')
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user.username} - {self.livre.titre}"


class Panier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, default='en cours')

    def total_panier(self):
        return sum(item.total() for item in self.items.all())

    def __str__(self):
        return f"Panier de {self.user.username}"


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='items')
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def total(self):
        return self.livre.prix * self.quantite

    def __str__(self):
        return f"{self.livre.titre} x {self.quantite}"


class Commande(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    adresse_livraison = models.TextField()
    date_commande = models.DateTimeField(auto_now_add=True)

    def total_commande(self):
        return sum(item.total() for item in self.items.all())

    def __str__(self):
        return f"Commande #{self.id} - {self.user.username}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    livre = models.ForeignKey(Livre, on_delete=models.SET_NULL, null=True)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=8, decimal_places=2)

    def total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.livre.titre} x {self.quantite}"
