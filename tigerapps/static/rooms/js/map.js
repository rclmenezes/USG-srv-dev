function initialize() {

    var half_expanded = true;

    var drawlocs = []
    // Butler
    drawlocs[1] = {"loc":new google.maps.LatLng(40.344168690579615, -74.6556450734024),
                   "zoom":17};
    // Forbes
    drawlocs[2] = {"loc":new google.maps.LatLng(40.341956723981475, -74.66061788891601),
                   "zoom":17};
    // Mathey
    drawlocs[3] = {"loc":new google.maps.LatLng(40.3474313111295, -74.6606876263504),
                   "zoom":17};
    // Rocky 
    drawlocs[4] = {"loc":new google.maps.LatLng(40.34811815850574, -74.66117042397308),
                   "zoom":17};
    // Upperclass
    drawlocs[5] = {"loc":new google.maps.LatLng(40.34586952499689, -74.65869206284331),
                   "zoom":16};
    // Whitman
    drawlocs[6] = {"loc":new google.maps.LatLng(40.34422593090207, -74.6579517731552),
                   "zoom":17};
    // Wilson
    drawlocs[7] = {"loc":new google.maps.LatLng(40.34563239200427, -74.65620833729552),
                   "zoom":17};

     var drawlocs_half = []
    // Butler
    drawlocs_half[1] = {"loc":new google.maps.LatLng(40.342824, -74.655629),
                   "zoom":17};
    // Forbes
    drawlocs_half[2] = {"loc":new google.maps.LatLng(40.340616723981475, -74.66061788891601),
                   "zoom":17};
    // Mathey
    drawlocs_half[3] = {"loc":new google.maps.LatLng(40.3460913111295, -74.6606876263504),
                   "zoom":17};
    // Rocky 
    drawlocs_half[4] = {"loc":new google.maps.LatLng(40.34677815850574, -74.66117042397308),
                   "zoom":17};
    // Upperclass
    drawlocs_half[5] = {"loc":new google.maps.LatLng(40.34300952499689, -74.65869206284331),
                   "zoom":16};
    // Whitman
    drawlocs_half[6] = {"loc":new google.maps.LatLng(40.34288593090207, -74.6579517731552),
                   "zoom":17};
    // Wilson
    drawlocs_half[7] = {"loc":new google.maps.LatLng(40.34429239200427, -74.65620833729552),
                   "zoom":17};

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
            displayFloorPlan(name);
        }
    }
    for (var i = 0; i < mapdata.length; i++) {
        markers[i] = new google.maps.Marker( 
            {
                position: new google.maps.LatLng(mapdata[i]['lat'], mapdata[i]['lon']),
                map: map,
                visible: false,
            });
        google.maps.event.addListener(markers[i], 'click', 
                                      clicklistener(mapdata[i]['name']));
    }
    
    google.maps.event.addListener(map, 'bounds_changed', function() 
    {
        //if (!map.getBounds().contains(marker.getPosition()))
        $('#testlatlng').html('center: ' + map.getCenter() + ' zoom: ' + map.getZoom());
    });

	
	/* map exapansion/contraction animation */
	var roomlist = document.getElementById("roomListWrapperBigger");
	document.getElementById("expandMap").addEventListener("click", function()
		{
            half_expanded = false;
            roomlist.style.height = '10%';
            $('#roomListTopTrim').css('margin-bottom','10%');
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
	document.getElementById("contractMap").addEventListener("click", function()
		{
            half_expanded = false;
            roomlist.style.height = '96%';
            $('#roomListTopTrim').css('margin-bottom','96%');
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
	document.getElementById("restoreMap").addEventListener("click", function()
		{
            half_expanded = true;
            roomlist.style.height = '50%';
            $('#roomListTopTrim').css('margin-bottom','50%');
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
    
    var switchdraw = function(e, drawid) {
        //console.log("id: " + drawid);
        for (var i = 0; i < mapdata.length; i++) {
            markers[i].setVisible(false);
            var draws = mapdata[i]['draws'];
            for (var j = 0; j < draws.length; j++)
                if (draws[j] == drawid)
                    markers[i].setVisible(true);
        }
        
        // Reset zoom and center depending on 
        // whether bottom table is expanded
        if (half_expanded)
        {
            map.panTo(drawlocs_half[drawid].loc);
            map.setZoom(drawlocs_half[drawid].zoom);
        }
        else
        {
            map.panTo(drawlocs[drawid].loc);
            map.setZoom(drawlocs[drawid].zoom);
        }
    }
    // Subscribe to needed events
    $.subscribe("draw", switchdraw);
    // Set the map to start draw
    switchdraw({}, 1);

}