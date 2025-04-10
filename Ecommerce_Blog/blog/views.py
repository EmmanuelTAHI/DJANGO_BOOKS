from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Article, Commentaire
from django.http import HttpResponseForbidden


def article_list(request):
    """Affiche la liste des articles publiés."""
    articles = Article.objects.filter(statut=True, date_de_publication__lte=timezone.now()).order_by(
        '-date_de_publication')
    return render(request, 'blog/article_list.html', {'articles': articles})


def article_detail(request, slug):
    """Affiche un article et ses commentaires, avec un formulaire pour commenter."""
    article = get_object_or_404(Article, slug=slug, statut=True, date_de_publication__lte=timezone.now())
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
            return redirect('blog:article_detail', slug=article.slug)
        else:
            return HttpResponseForbidden("Le commentaire ne peut pas être vide.")

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'commentaires': commentaires_principaux
    })


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
            return redirect('blog:article_detail', slug=article.slug)
    return redirect('blog:article_detail', slug=article.slug)