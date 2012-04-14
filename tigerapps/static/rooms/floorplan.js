function displayFloorPlan(name)
{
    var canvas = document.getElementById("map_canvas");
    canvas.innerHTML = "";
    canvas.appendChild(getFloorPlanImg(name));
}

function getFloorPlanImg(name)
{
    // TODO remove these
    var floorPlanImgWidth = 1200;
    var bldgId = "0007-00";
    var zoom = 1.0;
    
    var img = document.createElement("img");
    img.src = "static/rooms/images/floorplans/" + bldgId + "-001.jpg";
    img.width = floorPlanImgWidth;

    var imgmap = document.createElement("map");
    imgmap.name = bldgId + "_map";

    for(var roomName in floorplancoords[bldgId])
    {
	for(var r in floorplancoords[bldgId][roomName])
	{
	    var rectCoords = floorplancoords[bldgId][roomName][r];
	    for(var i in rectCoords)
	    {
		rectCoords[i] *= zoom;
		imgmap.appendChild(createMapArea(bldgId, roomName, rectCoords));
	    }
	}
    }
    img.useMap = "#" + imgmap.name;
    document.body.appendChild(imgmap);
    return img;
}

function createMapArea(bldgId, roomName, rectCoords)
{
    var area = document.createElement("area");
    area.shape = "rect";
    area.coords = rectCoords.join();
    area.onclick = function(){
	alert("displaying information for room: " + roomName);
    }
    return area;
}