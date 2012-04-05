function initialize() {
    var myOptions = {
        center: new google.maps.LatLng(40.346446, -74.657013),
        zoom: 16,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"),
                                  myOptions);
    var marker = new google.maps.Marker( {
        position: new google.maps.LatLng(40.344267, -74.654422),
        map: map,
    });
    
    google.maps.event.addListener(marker, 'click', function() {
        alert('You clicked on Scully!');
    });
    
    google.maps.event.addListener(map, 'bounds_changed', function() {
        if (!map.getBounds().contains(marker.getPosition()))
            alert('went out of bounds!');
    });
}