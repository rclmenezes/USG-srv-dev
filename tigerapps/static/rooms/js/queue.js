// Module for managing the queue panel

var ExternAjax = function(url, type, data, onSuccess) {
    console.log('in externajax');
    // xhr = $.ajax({
    //     url: REAL_TIME_ADDR + url,
    //     success: function(data) {
    //         alert('hello')
    //     },
    //     data: data,
    //     type: type,
    //     xhrFields: {
    //         withCredentials: true
    //     }
    // });
    xhr = $.ajax({
//        url:'trigger/',
        url: REAL_TIME_ADDR + url,
        type: 'POST',
        data: data,
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {onSuccess(JSON.parse(data))}
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
    var saveurl = REAL_TIME_ADDR + '/update_queue/'
    
    // Last update for this draw
    var update_timestamp = 0
    // Currently waiting request
    var update_xhr = 0
    
    // Update the idlist (i.e. after deletion, reordering)
    var update_idlist = function() {
        idlist = new Array();
        var stringarr = $('#room_queue').sortable('toArray');
        for (var i = 0; i < stringarr.length; i++)
            idlist[i] = parseInt(stringarr[i].substring(prefix.length));
    }

    // Add a room to the queue
    var add = function(e, roominfo) {
        // Check not already in list
        if (idlist.indexOf(roominfo['id']) != -1)
            return;
        idlist.push(roominfo['id']);
        var tag ='<li id="'+prefix+roominfo['id']+'" class="queued_room">';
        tag += roominfo['number'] + ' ' + roominfo['building'] + '</li>';
        $('#room_queue').append(tag);
        $('#room_queue').sortable('refresh');
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
        // console.log(idlist);
    }

    // Respond to reordering
    var reorder = function() {
        update_idlist();
        // console.log(idlist);
        save();
    }

    // Save the current list to the server
    var save = function() {
        //alert(current_draw);
        ExternAjax('/update_queue/'+current_draw, 'POST', {'queue':JSON.stringify(idlist)},
               function(data) {
                   console.log(data);
               });

        // $.post(saveurl+current_draw, {'queue':JSON.stringify(idlist)},
        //        function(data) {
        //            console.log(data);
        //        });
    }

    // Pull up the queue for a new draw
    // var switchhelper = function(data) {
    //     idlist = new Array();
    //     $('#room_queue').sortable('refresh');
    //     update_idlist();
    //     //console.log(idlist);
    // }
    var switchdraw = function(e, drawid) {
        //$('#room_queue').load('/get_queue/'+drawid, switchhelper);
        get_queue(drawid, 0);
	    $('#queuehead').html(drawdata[drawid-1]['name'] + ' Queue'); // needs to be more secure?
    }

    var handler = function(data) {
        console.log('got queue');
        idlist = new Array();
        console.log(data)
        update_timestamp = data.timestamp;
        // Put into list - formatting goes here
        $('#room_queue').html(JSON.stringify(data.rooms));
        $('#room_queue').sortable('refresh');
        update_idlist();
        //setInterval(get_update, 1);
    }

    var get_queue = function(drawid, timestamp) {
        if (update_xhr && update_xhr.readystate != 4)
            update_xhr.abort();
        console.log('Getting queue');
        update_xhr = ExternAjax('/get_queue/'+drawid+'/'+timestamp,
                                'json', null, handler);
    }

    var get_update = function() {
        get_queue(current_draw, update_timestamp);
    }

        
    // Subscribe to relevant events
    $.subscribe('queue/add', add);
    $.subscribe('queue/remove', remove);
    $.subscribe("draw", switchdraw);
    
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