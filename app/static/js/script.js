$(document).ready(function() {
    $('[data-bs-toggle="tooltip"]').tooltip();

    $('.table').on('click', '.btn-print', function(e) {
        e.preventDefault();
        window.print();
    });

    setTimeout(function() {
        $('.alert-dismissible').fadeOut('slow');
    }, 5000);
});
