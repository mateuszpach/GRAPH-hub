$('#user-filter-btn').click(function () {
    $('#user-filter').selectpicker('val', '');
});
$('#tags-filter-btn').click(function () {
    $('#tags-filter').selectpicker('val', '');
});
$('.like').click(function (event) {
    $.getJSON($SCRIPT_ROOT + '/graph/like', {
        graph_id: $(event.target).val()
    }, function (data) {
        if (data.status == 403) {
            $("#flash-container").html(
                '<div class="alert alert-danger">\n' +
                'Your must be logged in to like!\n' +
                '</div>');
        } else if (data.action == 'like') {
            $(event.target).addClass('btn-outline-success');
            $(event.target).removeClass('btn-outline-primary');
            $(event.target).html('<i class="fas fa-thumbs-up mr-2"></i>Liked');
        } else {
            $(event.target).addClass('btn-outline-primary');
            $(event.target).removeClass('btn-outline-success');
            $(event.target).html('<i class="fas fa-thumbs-up mr-2"></i>Like');
        }
        return false;
    });
});
