function initialize() {
    var myOptions = 
    {
        center: new google.maps.LatLng(40.346446, -74.657013),
        zoom: 16,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    var markers = new Array();
    var clicklistener = function(name) {
        return function() {
            alert(name);
        }
    }
    for (var i = 0; i < mapdata.length; i++) {
        markers[i] = new google.maps.Marker( 
            {
                position: new google.maps.LatLng(mapdata[i]['lat'], mapdata[i]['lon']),
                map: map,
            });
        google.maps.event.addListener(markers[i], 'click', 
                                      clicklistener(mapdata[i]['name']));
    }
    var marker = new google.maps.Marker( 
    {
        position: new google.maps.LatLng(40.344267, -74.654422),
        map: map,
    });
    
    google.maps.event.addListener(marker, 'click', function() 
    {
        console.log('You clicked on Scully!');
    });

    google.maps.event.addListener(map, 'bounds_changed', function() 
    {
        if (!map.getBounds().contains(marker.getPosition()))
            console.log('went out of bounds!');
    });

	
	/* map exapansion/contraction animation */
	var tophalf = document.getElementById("top_half");
	var datap = document.getElementById("dataPanel");
    var buffer = document.getElementById("middle_buffer");
	document.getElementById("expandMap").addEventListener("click", function()
		{
		    tophalf.style.height = "86.75%"; 
		    datap.style.height="11.75%";
            buffer.style.display="block";
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
	document.getElementById("contractMap").addEventListener("click", function()
		{
		    tophalf.style.height = "0%"; 
		    datap.style.height="100%";
            buffer.style.display="none";
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
	document.getElementById("restoreMap").addEventListener("click", function()
		{
		    tophalf.style.height = "49.25%"; 
		    datap.style.height="49.25%";
            buffer.style.display="block";
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
    
    var switchdraw = function(e, drawid) {
        for (var i = 0; i < mapdata.length; i++) {
            console.log("id: " + drawid);
            markers[i].setVisible(false);
            var draws = mapdata[i]['draws'];
            for (var j = 0; j < draws.length; j++)
                if (draws[j] == drawid)
                    markers[i].setVisible(true);
        }
    }
    // Subscribe to needed events
    $.subscribe("draw", switchdraw);

}