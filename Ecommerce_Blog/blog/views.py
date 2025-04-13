from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Article, Commentaire
from django.http import HttpResponseForbidden
from django.utils import timezone

# ==============================
# 📝 Pages Blog
# ==============================

def blog_detail(request):
    article = get_object_or_404(Article, statut=True, date_de_publication__lte=timezone.now())
    commentaires_principaux = article.commentaires.filter(parent_id__isnull=True, statut=True).order_by('created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        contenu = request.POST.get('contenu')
        parent_id = request.POST.get('parent_id')  # ID du commentaire parent, si c'est une réponse
        if contenu:
            commentaire = Commentaire(
                article=article,
                auteur_id=request.user,
                contenu=contenu,
                parent_id=Commentaire.objects.get(id=parent_id) if parent_id else None
            )
            commentaire.save()
            return redirect('blog:blog-detail')
        else:
            return HttpResponseForbidden("Le commentaire ne peut pas être vide.")

    return render(request, 'blog/blog-detail.html', {'article': article, 'commentaires': commentaires_principaux })

def blog_grid_left_sidebar(request):
    articles = Article.objects.filter(est_publie=True)
    return render(request, 'blog/blog-grid-left-sidebar.html',{'articles': articles})

def blog_grid_no_sidebar(request):
    return render(request, 'blog/blog-grid-no-sidebar.html')

@login_required
def add_comment(request, article_slug):
    """Vue alternative pour ajouter un commentaire (si tu veux séparer la logique)."""
    article = get_object_or_404(Article, slug=article_slug, statut=True)
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        parent_id = request.POST.get('parent_id')
        if contenu:
            commentaire = Commentaire(
                article=article,
                auteur_id=request.user,
                contenu=contenu,
                parent_id=Commentaire.objects.get(id=parent_id) if parent_id else None
            )
            commentaire.save()
            return redirect('blog:blog-detail', slug=article.slug)
    return redirect('blog:blog-detail', slug=article.slug)