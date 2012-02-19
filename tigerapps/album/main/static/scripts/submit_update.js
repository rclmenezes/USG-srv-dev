var numimages = 30;
var xC = 40.345748;
var yC = -74.655472;
var xd = 0.01;
var yd = 0.01;
var initialcenter = new google.maps.LatLng(xC,yC);
var initialbounds = new google.maps.LatLngBounds(new google.maps.LatLng(xC-xd, yC-yd), new google.maps.LatLng(xC+xd, yC+yd));
var map;
var lastPoint = null;
var lastMarker = null;

function checkbounds() {
    if (initialbounds.contains(map.getCenter())) return;

    var c = map.getCenter();
    x = c.lng();
    y = c.lat();
    maxX = initialbounds.getNorthEast().lng();
    maxY = initialbounds.getNorthEast().lat();
    minX = initialbounds.getSouthWest().lng();
    minY = initialbounds.getSouthWest().lat();

    if (x < minX) x = minX;
    if (x > maxX) x = maxX;
    if (y < minY) y = minY;
    if (y > maxY) y = maxY;

    map.setCenter(new google.maps.LatLng(y, x));
}

$(document).ready(function() {
    var options = {
        zoom: 16,
        maxZoom: 22,
        minZoom: 16,
        mapTypeControl: false,
        streetViewControl: false,
        center: initialcenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }

    map = new google.maps.Map($("#map")[0], options);
    google.maps.event.addListener(map, 'center_changed', checkbounds);
    google.maps.event.addListener(map, 'idle', start);
    
    $('form').submit(function(event) {
        var x = $('input[name="xpos"]', this).val();
        var y = $('input[name="ypos"]', this).val();
        if (!lastMarker) {
            $('p.error').show();
            event.preventDefault();
            return false;
        }
    });
});

function start() {
    google.maps.event.clearListeners(map, 'idle');
    // make a thumbnail icon
    var thumbnail = $('input[name="thumbnail"]').val();
    var oldheight = $('input[name="height"]').val();
    var oldwidth = $('input[name="width"]').val();
    var width;
    var height;
    var maxsize = 60;
    if (width > height) {
        width = maxsize;
        height = oldheight / (oldwidth / maxsize);
    }
    else {
        height = maxsize;
        width = oldwidth / (oldheight / maxsize);
    }
    width = Math.round(width);
    height = Math.round(height);
    var markerimage = new google.maps.MarkerImage(
        '/'+thumbnail,
        new google.maps.Size(width,height),
        new google.maps.Point(0,0),
        new google.maps.Point(Math.round(width/2),Math.round(height/2)),
        new google.maps.Size(width,height)
    );
    
    var ixpos = $('input[name="xpos"]').val();
    var iypos = $('input[name="ypos"]').val();
    // if pic was geotagged
    if (ixpos != "" && iypos != "") {
        $('input[type="submit"]').removeAttr('disabled');
        lastPoint = new google.maps.LatLng(parseFloat(ixpos), parseFloat(iypos));
        lastMarker = new google.maps.Marker({
            position : lastPoint,
            map : map,
            icon : markerimage,
            clickable : false,
            draggable : true,
            raiseOnDrag : false,
            animation: google.maps.Animation.DROP,
        });
    }
    // if pic was not geotagged
    else {
        lastPoint = new google.maps.LatLng(40.345748,-74.655472);
        lastMarker = new google.maps.Marker({
            position : lastPoint,
            map : map,
            icon : markerimage,
            clickable : false,
            draggable : true,
            raiseOnDrag : false,
        });
    }
    // when the marker is moves
    google.maps.event.addListener(lastMarker, 'dragend', changePos);
}

function changePos() {
    lastPointer = lastMarker.getPosition();
    var x = lastPointer.lat();
    var y = lastPointer.lng();
    $('input[name="xpos"]').val(x);
    $('input[name="ypos"]').val(y);
    $('input[type="submit"]').removeAttr('disabled');
}
