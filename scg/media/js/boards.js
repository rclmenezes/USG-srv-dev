display_board = function(board, data) {
    if(!board.focused && !board.saving) {
        board.val(data);
    }
};

get_board = function(board) {
    if(!board.focused && !board.saving) {
        $.get(board.get_url, {}, function(data) {
            display_board(board, data);
        });
    }

    window.setTimeout(get_board, board.get_interval, board);
}

save_board = function(board) {
    board.saving = true;
    $.post(board.save_url, {"board": board.val() }, function() {
            if(board.changed) {
                board.changed = false;
                save_board(board);
            }
            board.saving = false;
        });
};

initialize_board = function(board, get_url, save_url, get_interval) {
    board.get_url = get_url
    board.save_url = save_url
    board.get_interval = get_interval

    board.focused = false;
    board.focus( function() { $(this).focused = true; } )
    board.blur( function() { $(this).focused = false; } )

    board.changed = false;
    board.saving = false;

    board.keyup(function() {
        if(!board.saving) {
            save_board(board);
        } else {
            board.changed = true;
        }
    });

    get_board(board);
}
