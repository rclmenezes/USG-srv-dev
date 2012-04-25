function displayFloorPlan(name)
{
    console.log("Floor plan for: " + name);
    var canvas = document.getElementById("map_canvas");
    //canvas = $("map_canvas");
    // console.log("width: " + canvas.outerWidth());
    //console.log("width: " + canvas.style.width);
    canvas.innerHTML = "";
    canvas.appendChild(getFloorPlanImg(name));
    //canvas.append(getFloorPlanImg(name));
}

function getFloorPlanImg(name)
{
    console.log(pdfByBldg);
    // Some buildings start with floor 0, while other start with 1
    var bldgId = pdfByBldg[name][0];
    if(! bldgId)
	bldgId = pdfByBldg[name][1];
    console.log(bldgId);

    // TODO make this changeable
    var zoom = 945.0/1200;
    
    var img = document.createElement("img");
    img.src = "static/rooms/images/floorplans/" + bldgId + "-001.jpg";
    img.width = floorplancoordsWidth * zoom;

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
	    }
	    imgmap.appendChild(createMapArea(bldgId, roomName, rectCoords));
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