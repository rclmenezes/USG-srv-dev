// Module for managing the queue panel

var QueueModule = (function($) {
    
    // The current ordered list of room ids
    var idlist = new Array();
    // The prefix for room ids in the queue elements
    var prefix = 'queue-';
    
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
        var tag ='<li id="'+prefix+roominfo['id']+'" class="ui-state-default">';
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
        $.post('/update_queue/'+current_draw, {'queue':JSON.stringify(idlist)});
        // function(data) {
        //     $('#testoutput').html(data);
        // });
    }

    // Pull up the queue for a new draw
    var switchhelper = function() {
        idlist = new Array();
        $('#room_queue').sortable('refresh');
        update_idlist();
        //console.log(idlist);
    }
    var switchdraw = function(e, drawid) {
        $('#room_queue').load('/get_queue/'+drawid, switchhelper);
	$('#queuehead').html('Current Queue: ' + drawdata[drawid-1]['name']); // needs to be more secure?
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