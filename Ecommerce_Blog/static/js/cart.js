$(document).ready(function() {
    // Récupérer le token CSRF depuis un input caché ou une meta tag
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val() || document.querySelector('meta[name="csrf-token"]').content;

    // Fonction pour afficher une notification
    function showNotification(message) {
        var $notification = $('#notification');
        $('#notification-message').text(message);
        $notification.fadeIn();

        // Masquer après 3 secondes
        setTimeout(function() {
            $notification.addClass('fade-out');
            setTimeout(function() {
                $notification.fadeOut().removeClass('fade-out');
            }, 500);
        }, 3000);

        // Fermer manuellement avec le bouton
        $('.notification-close').on('click', function() {
            $notification.addClass('fade-out');
            setTimeout(function() {
                $notification.fadeOut().removeClass('fade-out');
            }, 500);
        });
    }

    // Ajouter au panier
    $('.add-to-cart-btn').on('click', function(e) {
        e.preventDefault();
        var livreId = $(this).data('livre-id');
        var button = $(this);

        $.ajax({
            url: "/add-to-cart/" + livreId + "/",
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                console.log('Response:', response);
                if (response.status === 'added' || response.status === 'updated') {
                    // Incrémenter le badge du panier
                    var badge = $('.badge-cart');
                    var currentCount = parseInt(badge.text()) || 0;
                    badge.text(currentCount + 1);
                    showNotification(response.message);
                }
            },
            error: function(xhr) {
                console.log('Error:', xhr.responseText);
                showNotification('Erreur lors de l\'ajout au panier.');
            }
        });
    });

    // Retirer du panier
    $('.remove-from-cart-btn').on('click', function(e) {
        e.preventDefault();
        var livreId = $(this).data('livre-id');
        var button = $(this);

        $.ajax({
            url: "/remove-from-cart/" + livreId + "/",
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                console.log('Response:', response);
                if (response.status === 'removed') {
                    // Supprimer la ligne du DOM
                    button.closest('tr[data-livre-id="' + livreId + '"]').fadeOut(500, function() {
                        $(this).remove();
                        // Vérifier si le panier est vide
                        if ($('.check-tbl tbody tr').length === 0) {
                            $('.check-tbl tbody').append('<tr><td colspan="6">Votre panier est vide.</td></tr>');
                        }
                    });
                    // Décrémenter le badge du panier
                    var badge = $('.badge-cart');
                    var currentCount = parseInt(badge.text()) || 0;
                    if (currentCount > 0) {
                        badge.text(currentCount - 1);
                    }
                    showNotification(response.message);
                } else if (response.status === 'error') {
                    showNotification(response.message);
                }
            },
            error: function(xhr) {
                console.log('Error:', xhr.responseText);
                showNotification('Erreur lors du retrait du panier.');
            }
        });
    });
});