// Code to handle the details popup that appears when you click on a
// photo on the map in addition to all the comments (posting,
// validating, replying, reporting) jazz.

var currentid;

function initcomments(form) {
    // On textarea focus, reveal the rest of the form a la Facebook.
    $('textarea', form).focus(function() {
        // If this is the default comment form, remove all the reply
        // forms.
        if (!form.hasClass('reply_form')) {
            $('.reply_form', form.parents('section')).remove();
        }
        $('label, input', form).show();
    });

    // handle for comment submission
    $("input[type='button']", form).click(function(){
        submitcomment(form);
    });

    // handle enter keypresses correctly
    $(form).submit(function(event) {
        event.preventDefault();
        $("input[type='button']", this).click();
        event.stopPropagation();
    });

    // warn users about invalid comment data
    $("textarea[name='comment']").keydown(function(event) {
        var length = $(this).val().length;
        var form = $(this).parents('form');
        if (length > 250) {
            $(".error", form)
                .show()
                .text("Comments must be 250 characters or fewer!");
            $("input[type='button']", form).attr("disabled", "disabled");
        }
        else {
            $(".error", form).hide();
            $("input[type='button']", form).removeAttr("disabled");
        }
    });
}

function initreplies(section) {
    // handler for reporting comments
    $(".report", section).click(function(event) {
        var article = $(this).parents('article');
        var id = $(article).data('id');
        var span = $('<span>Reporting...</span>');
        $(this).replaceWith(span);

        $.ajax({
            url: 'api/report_comment.json',
            data: { id: id },
            success: function(data) {
                alert('Number of times flagged: ' + data);
                $(span).text('Reported');
            }
        });
    });

    // handler for replying to comments
    $('a.reply', section).click(function() {
        // hide all other reply forms
        $('.reply_form', section).remove();

        // clone the default comment form
        var form = $('#comment_form', section).clone();
        form.removeAttr('id');
        form.addClass('reply_form');
        form.css('padding-left', '30px');

        // jot down the parent comment's id and add the form after the
        // parent article
        var article = $(this).parents('article');
        var parent = $(article).data('id');
        $('input[name="parentid"]', form).val(parent);
        form.css('margin-left', article.css('margin-left'));
        $(article).after(form);

        // initialize the form
        initcomments(form);
    });
}

function updatecomments(form) {
    var photoid = $("input[name='id']", form).val();
    $.ajax({
        url: "api/comments.html",
        data: { id: photoid },
        success: function(text) {
            var section = form.parents('section');
            $(".replaceme", section).html(text);
            initreplies(section);
        }
    });
}

function submitcomment(form) {
    var author = $("input[name='author']", form).val();
    var comment = $("textarea", form).val();
    var photoid = $("input[name='id']", form).val();
    var parent = $("input[name='parentid']", form).val();
    var indicator = $(".indicator", form);

    // construct the parameters
    var data = {
        id: photoid,
        author: author,
        comment: comment,
    };
    if (parent) {
        data.parent = parent;
    }

    $("input[name='author']", form).val("");
    $("textarea", form).val("");
    indicator.show();

    $.ajax({
        type: 'POST',
        url: "api/submit_comment.json",
        data: data,
        success: function(data, textstatus) {
            if (data != "") {
                alert(data);
            }
            updatecomments(form);
            indicator.hide();
        },
        error: function() {
            alert("This photo seems to be unavailable or has been deleted by the moderators. We apologize for the inconvenience");
            window.location='/';
            indicator.hide();
        }
    });
}

function nextdetails() {
    var length = shownids.length;
    var index = shownids.indexOf(currentid);
    var id = (index + 1) % length;
    showdetails(shownids[id]);
}

function prevdetails() {
    var length = shownids.length;
    var index = shownids.indexOf(currentid);
    var id;
    if (index == 0) {
        id = length - 1;
    }
    else {
        id = (index - 1) % length;
    }
    showdetails(shownids[id]);
}

function showdetails(id) {
    $.ajax({
        url: 'api/details.json?id='+id,
        success: function(responseText){
            // Reset DOM state.
            $('#DOMWindow').html("");
            $('#hidden_details').html("");

            // New state!
            currentid = id;
            $('#hidden_details').html(responseText);
            document.title = $('input[name="title"]').val();
            $.openDOMWindow({
                width: $(window).width() * 0.75,
                windowSourceID: '#hidden_details',
                windowBGColor: "white",
            });
            $.history.load(id);
        },
        error: function(){
            alert("This photo seems to be unavailable or has been deleted by the moderators. We apologize for the inconvenience");
            window.location='/';
        },
        async: false
    });
    FB.Event.subscribe('edge.create', function (resp) {
        $.ajax({
            url: 'api/like.json?id='+id,
        });
    });

    // handler for reporting image
    $("#report_image").change(function() {
        var reason = $(this).val();
        if (reason == '0') return;

        var span = $('<span>Reporting...</span>');
        $(this).replaceWith(span);
        $.ajax({
            url: 'api/report_image.json',
            data: { id: currentid, reason: reason },
            success: function(data) {
                alert("Number of times flagged: " + data);
                $(span).text('Reported!');
            },
        });
    });

    // set up event handlers for comments
    initcomments($('section.comments form'));
    initreplies($('section.comments'));
}
