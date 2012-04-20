$(function() {
    $('.queue_drag').sortable({
            revert:true
    });

    $('#list_queues').accordion();

    $("ul, li").disableSelection();
});