// Module for managing the queue panel

var ExternAjax = function(url, type, data, onSuccess, onFail) {
    console.log('in externajax');
    xhr = $.ajax({
        url: REAL_TIME_ADDR + url,
        type: 'POST',
        data: data,
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {console.log(data);onSuccess(JSON.parse(data))},
        error: onFail
    });
    console.log(xhr);
    return xhr;
}
var QueueModule = (function($) {
    
    // The current ordered list of room ids
    var idlist = new Array();
    // The prefix for room ids in the queue elements
    var prefix = 'queue-';
    // URL for saving updates
    var saveurl = REAL_TIME_ADDR + '/update_queue/';
    
    // Last update for this draw
    var update_timestamp = 0;
    // Currently waiting request
    var update_xhr = 0;
    // Are we sending queue
    var update_lock = false;
    
    // Update the idlist (i.e. after deletion, reordering)
    var update_idlist = function() {
        idlist = new Array();
        var stringarr = $('#room_queue').sortable('toArray');
        for (var i = 0; i < stringarr.length; i++)
            idlist[i] = parseInt(stringarr[i].substring(prefix.length));
        console.log('in update_idlist');
        console.log(idlist);
    }

    var add_helper = function(rooms) {
        rooms = [].concat(rooms);
        for ( var i in  rooms) {
            room = rooms[i];
            // Check not already in list
            if (idlist.indexOf(room.id) != -1)
                continue;
            idlist.push(room.id);
            var tag = '<li id="queue-'+room.id+'" class="queued_room">';
            tag  += '<a class="fancyroom link_in_queue" title="Room Overview" data-fancybox-type="iframe" href="/get_room/'+room.id+'">'+room.number+' '+room.building+'</a>';
            tag += '<div onclick="$.publish(\'queue/remove\','+room.id+')" title="Remove from queue" class="removeRoom removeInQueue" ></div> </li>';
            $('#room_queue').append(tag);
            $.publish('mark_as_neg', room.id);
        }
        $('#room_queue').sortable('refresh');
        // update_idlist();
    }

    // Add a room to the queue
    var add = function(e, rooms) {
        add_helper(rooms);
        save();
    }

    // Remove a room from the queue
    var remove = function(e, roomid) {

        if (idlist.indexOf(roomid) == -1)
            return;
        $('#'+prefix+roomid).remove();
        $('#room_queue').sortable('refresh');
        update_idlist();
        save();

        console.log('markaspos - '+roomid);
        // console.log(idlist);
        $.publish('mark_as_pos', roomid);
        console.log('markaspos2 - '+roomid);
    }

    var clear = function() {
        console.log('in clear')
        console.log(idlist)
        for ( var i = 0; i < idlist.length; i++) {
            console.log('marking '+idlist[i]);
            $.publish('mark_as_pos', idlist[i]);
            //mark_as_pos({}, idlist[i]);
        }
        idlist=[];
        $('#room_queue').html('');
        $('#room_queue').sortable('refresh');
    }
        
    
    var mark_as_neg = function(e, roomid) {
        $('#add'+roomid).hide();
        $('#remove'+roomid).show();
    }

    var mark_as_pos = function(e, roomid) {
        console.log('mark as pos ' +  roomid);
        $('#add'+roomid).show();
        $('#remove'+roomid).hide();
    }

    // Respond to reordering
    var reorder = function() {
        update_idlist();
        // console.log(idlist);
        save();
    }

    // Save the current list to the server
    save = function() {
        ExternAjax('/update_queue/'+current_draw, 'POST', {'queue':JSON.stringify(idlist)},
               function(data) {
                   console.log(data);
               });
    }
    var switchdraw = function(e, drawid) {
        //$('#room_queue').load('/get_queue/'+drawid, switchhelper);
        get_queue(drawid, 0);
	    $('#queuehead').html(drawdata[drawid-1]['name'] + ' Queue'); // needs to be more secure?
    }

    var handler = function(data) {
        console.log('got queue');
        console.log(data)
        update_timestamp = data.timestamp;
        clear();
        add_helper(data.rooms);
        if (data.kind == 'EDIT')
            $('#queue_note').html(data.netid + ' edited queue');
        else
            $('#queue_note').html('new queue');
        update_idlist();
        setTimeout(get_update, 100);
    }


    var get_queue = function(drawid, timestamp) {
        if (update_xhr && update_xhr.readystate != 4)
            update_xhr.abort();
        console.log('Getting queue');
        update_xhr = ExternAjax('/get_queue/'+drawid+'/'+timestamp,
                                'json', null, handler);
                                //function(){setTimeout(get_update, 1000)});
    }

    get_update = function() {
        console.log('get_update called');
        get_queue(current_draw, update_timestamp);
    }

        
    // Subscribe to relevant events
    $.subscribe('queue/add', add);
    $.subscribe('queue/remove', remove);
    $.subscribe("draw", switchdraw);
    $.subscribe('mark_as_neg', mark_as_neg);
    $.subscribe('mark_as_pos', mark_as_pos);
    
    // Set up the draggable queue
    $(function() {
        $('#room_queue').sortable({
            revert:true,
            stop:reorder
        });
        $('#list_queues').accordion();
        $("ul, li").disableSelection();
    });

}(jQuery));


var avail_handler = function(data) {
    console.log('In avail_handler');
    console.log(data);
    for (var i = 0; i < data.rooms.length; i++) {
        console.log(data.rooms[i]);
        console.log($('#avail-'+data.rooms[i]));
        $('#avail-'+data.rooms[i]).html('No');
    }
    setTimeout(function() {check_avail(data.timestamp)}, 100);
}
var check_avail = function(timestamp) {
    ExternAjax('/check_availability/'+timestamp, 'GET', null, avail_handler)
}

check_avail(0);
