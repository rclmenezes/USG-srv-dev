var FLOOR_PLAN_ZOOM_LEVELS = [.4, .55, .7, .85, 1, 1.15, 1.3];
var FLOOR_PLAN_DEFAULT_ZOOM = 3;

function displayFloorPlan(name)
{
    console.log("Floor plan for: " + name);
    var map_canvas = document.getElementById("map_canvas");
    var fp_canvas = document.getElementById("floorplan_canvas");
    var bldgId;
    var current_zoom = FLOOR_PLAN_DEFAULT_ZOOM;


    
    map_canvas.style.display = "none";
    fp_canvas.style.display = "inline";

    fp_canvas.innerHTML = "";
    fp_canvas.appendChild(getFloorPlanImg(name));
    fp_canvas.appendChild(getBackButton());
    fp_canvas.appendChild(getZoomInButton());
    fp_canvas.appendChild(getZoomOutButton());

    function getFloorPlanImg(name)
    {
	// Some buildings start with floor 0, while other start with 1
	// Let's just always start at floor 1 
	bldgId = pdfByBldg[name][1];

	var default_zoom = FLOOR_PLAN_ZOOM_LEVELS[FLOOR_PLAN_DEFAULT_ZOOM];
    
	var img = document.createElement("img");
	img.src = "static/rooms/images/floorplans/" + bldgId + "-001.jpg";
	img.width = floorplancoordsWidth * default_zoom;
	img.id = "floorplan_img";

	var imgmap = getFloorPlanImgMap(default_zoom);
	img.useMap = "#" + imgmap.name;

	return img;
    }

    function getFloorPlanImgMap(zoom)
    {
	var imgmap = document.createElement("map");
	imgmap.name = bldgId + "_map";
	imgmap.id = bldgId + "_map";

	for(var roomName in floorplancoords[bldgId])
	{
	    for(var r in floorplancoords[bldgId][roomName])
	    {
		
		var rectCoords = [];
		for(var i in floorplancoords[bldgId][roomName][r])
		{
		    rectCoords[i] = zoom * floorplancoords[bldgId][roomName][r][i];
		    rectCoords[i] = parseInt(rectCoords[i]);
		}
		console.log(rectCoords);
		imgmap.appendChild(getMapArea(bldgId, roomName, rectCoords));
	    }
	}

	document.body.appendChild(imgmap);
	return imgmap;
    }

    function getMapArea(bldgId, roomName, rectCoords)
    {
	var area = document.createElement("area");
	area.shape = "rect";
	area.coords = rectCoords.join();
	area.onclick = function(){
	    alert("displaying information for room: " + roomName);
	}
	return area;
    }

    function resizeFloorPlan(zoom)
    {
	var img = document.getElementById("floorplan_img");
	var oldmap = document.getElementById(bldgId + "_map");
	
	img.width = floorplancoordsWidth * zoom;

	// Remove old image map.
	oldmap.parentNode.removeChild(oldmap);

	// Now create a new image map.
	getFloorPlanImgMap(zoom);
    }

    function getBackButton()
    {
	var button = document.createElement("span");
	button.innerHTML = "<< back"; // TODO make this prettier
	button.id = "fp_back_button";
	button.className = "fp_button";
	button.onclick = function()
	{
	    fp_canvas.style.display = "none";
	    map_canvas.style.display = "inline";
	}
	return button;
    }

    function getZoomInButton()
    {
	var button = document.createElement("span");
	button.innerHTML = "+ zoom in"; // TODO make this prettier
	button.id = "fp_zoomin_button";
	button.className = "fp_button";

	button.onclick = function()
	{
	    if(current_zoom < FLOOR_PLAN_ZOOM_LEVELS.length - 1)
	    {
		current_zoom++;
		resizeFloorPlan(FLOOR_PLAN_ZOOM_LEVELS[current_zoom]);
	    }
	}
	return button;
    }

    function getZoomOutButton()
    {
	var button = document.createElement("span");
	button.innerHTML = "- zoom out"; // TODO make this prettier
	button.id = "fp_zoomout_button";
	button.className = "fp_button";
	
	button.onclick = function()
	{
	    if(current_zoom > 0)
	    {
		current_zoom--;
		resizeFloorPlan(FLOOR_PLAN_ZOOM_LEVELS[current_zoom]);
	    }
	}
	return button;
    }

}