$(document).ready(function() {
    // Récupérer le token CSRF
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val() || document.querySelector('meta[name="csrf-token"]').content;

    var isProcessing = false; // Flag pour éviter les double clics

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

    // Ajouter ou retirer de la wishlist
    $('.add-to-wishlist').on('click', function(e) {
        e.preventDefault(); // Empêche le changement automatique de l'état
        if (isProcessing) return;
        isProcessing = true;

        var checkbox = $(this);
        var livreId = checkbox.data('livre-id');

        console.log('Book ID clicked:', livreId);

        $.ajax({
            url: "/add-to-wishlist/",  // URL statique, ajuster si nécessaire
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'livre_id': livreId,
            },
            success: function(response) {
                console.log('Response:', response);
                var badge = $('.badge-wishlist');
                var currentCount = parseInt(badge.text()) || 0;

                if (response.status === 'added') {
                    checkbox.prop('checked', true);
                    badge.text(currentCount + 1);
                    showNotification(response.message || 'Livre ajouté à la wishlist.');
                } else if (response.status === 'removed') {
                    checkbox.prop('checked', false);
                    if (currentCount > 0) {
                        badge.text(currentCount - 1);
                    }
                    showNotification(response.message || 'Livre retiré de la wishlist.');
                }
            },
            error: function(xhr) {
                console.log('Error:', xhr.responseText);
                showNotification('Erreur lors de la mise à jour de la wishlist.');
            },
            complete: function() {
                isProcessing = false; // Réactive le clic après traitement
            }
        });
    });
});
