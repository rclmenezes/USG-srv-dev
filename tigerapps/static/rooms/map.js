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
	var mapc = document.getElementById("map_canvas");
	var datap = document.getElementById("dataPanel");
	document.getElementById("expandMap").addEventListener("click", function()
		{
		    mapc.style.height = "80%"; 
		    datap.style.height="20%";
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
	document.getElementById("contractMap").addEventListener("click", function()
		{
		    mapc.style.height = "0%"; 
		    datap.style.height="100%";
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })
	document.getElementById("restoreMap").addEventListener("click", function()
		{
		    mapc.style.height = "50%"; 
		    datap.style.height="50%";
		    setTimeout(function(){google.maps.event.trigger(map, 'resize');}, 300);
	    })


}