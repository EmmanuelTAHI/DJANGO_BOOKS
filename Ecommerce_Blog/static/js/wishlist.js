$(document).ready(function() {
    // Récupérer le token CSRF
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val() || document.querySelector('meta[name="csrf-token"]').content;

    // Fonction pour afficher une notification
    function showNotification(message) {
        var $notification = $('#notification');
        $('#notification-message').text(message);
        $notification.fadeIn();

        setTimeout(function() {
            $notification.addClass('fade-out');
            setTimeout(function() {
                $notification.fadeOut().removeClass('fade-out');
            }, 500);
        }, 3000);

        $('.notification-close').on('click', function() {
            $notification.addClass('fade-out');
            setTimeout(function() {
                $notification.fadeOut().removeClass('fade-out');
            }, 500);
        });
    }

    // Ajouter à la wishlist (depuis un bouton/checkbox)
    $('.add-to-wishlist').on('click', function(e) {
        e.preventDefault();
        var checkbox = $(this);
        var livreId = checkbox.data('livre-id');

        $.ajax({
            url: "/add-to-wishlist/",
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'livre_id': livreId,
            },
            success: function(response) {
                console.log('Response:', response);

                if (response.status === 'added') {
                    var badge = $('.badge-wishlist');
                    var currentCount = parseInt(badge.text()) || 0;
                    checkbox.prop('checked', true);
                    badge.text(currentCount + 1);
                    showNotification(response.message || 'Ajouté à la wishlist.');
                } else if (response.status === 'removed') {
                    checkbox.prop('checked', false);
                    if (currentCount > 0) {
                        badge.text(currentCount - 1);
                    }
                    showNotification(response.message || 'Retiré de la wishlist.');
                }
            },
            error: function(xhr) {
                console.log('Erreur:', xhr.responseText);
                showNotification("Erreur lors de la mise à jour de la wishlist.");
            }
        });
    });

    // Retirer de la wishlist depuis la page wishlist
    $('.remove-from-wishlist-btn').on('click', function(e) {
        e.preventDefault();
        var button = $(this);
        var livreId = button.data('livre-id');

        $.ajax({
            url: "/remove-from-wishlist/" + livreId + "/",
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

                        // Si la wishlist est vide
                        if ($('.check-tbl tbody tr').length === 0) {
                            $('.check-tbl tbody').append('<tr><td colspan="6">Votre wishlist est vide.</td></tr>');
                        }

                        // Décrémenter le badge
                        var badge = $('.badge-wishlist');
                        var currentCount = parseInt(badge.text()) || 0;
                        if (currentCount > 0) {
                            badge.text(currentCount - 1);
                        }
                    });

                    showNotification(response.message || 'Livre retiré de la wishlist.');
                } else {
                    showNotification(response.message || 'Erreur lors du retrait de la wishlist.');
                }
            },
            error: function(xhr) {
                console.log('Erreur:', xhr.responseText);
                showNotification('Erreur lors de la requête.');
            }
        });
    });
});
