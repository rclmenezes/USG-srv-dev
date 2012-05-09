var FLOOR_PLAN_ZOOM_LEVELS = [.4, .55, .7, .85, 1, 1.2, 1.5, 2];
var FLOOR_PLAN_DEFAULT_ZOOM = 1;

function displayFloorPlan(name, floor)
{
    console.log("Floor plan for: " + name);
    var map_canvas = document.getElementById("map_canvas");
    var fp_canvas = document.getElementById("floorplan_canvas");
    var bldgId;
    var current_zoom = FLOOR_PLAN_DEFAULT_ZOOM;
    var current_view_pos = {x: 0, y: 0};
    var mousedown_pos = undefined; 

    if(! floor)
	floor = 1;
    
    map_canvas.style.display = "none";
    fp_canvas.style.display = "inline";

    fp_canvas.style.height = "100%";
    fp_canvas.style.width = "100%";


    fp_canvas.innerHTML = "";
    fp_canvas.appendChild(getFloorPlanImg(name));
    fp_canvas.appendChild(getBackButton());
    fp_canvas.appendChild(getZoomInButton());
    fp_canvas.appendChild(getZoomOutButton());
    fp_canvas.appendChild(getFloorUpButton());
    fp_canvas.appendChild(getFloorDownButton());

    function getFloorPlanImg(name)
    {
	
	bldgId = pdfByBldg[name][floor];

	var default_zoom_factor = FLOOR_PLAN_ZOOM_LEVELS[FLOOR_PLAN_DEFAULT_ZOOM];

	var img = document.createElement("img");
	img.src = "static/rooms/images/floorplans/" + bldgId + "-001.jpg";
	img.style.width = floorplancoordsWidth * default_zoom_factor + "px";
	img.id = "floorplan_img";

	var imgmap = getFloorPlanImgMap(FLOOR_PLAN_DEFAULT_ZOOM);
	img.useMap = "#" + imgmap.name;

	img.onmousedown = function(ev)
	{
	    mousedown_pos = {x: ev.clientX, y: ev.clientY};
	    img.style.cursor = "-moz-grabbing";
	};

	img.onmouseup = handleMouseDrag;

	// Disable browser's default drag and drop
	img.ondragstart = function() { return false; };

	return img;
    }

    function handleMouseDrag(ev)
    {

	if(! mousedown_pos)
	    return;

	if((ev.clientX == mousedown_pos.x)
	   && (ev.clientY == mousedown_pos.y))
	{
	    mousedown_pos = undefined;
	    return;
	}

	var zoom_factor = FLOOR_PLAN_ZOOM_LEVELS[current_zoom];
	var width = floorplancoordsWidth * zoom_factor;
	var height = width * this.height / this.width;
	  
	current_view_pos.x += mousedown_pos.x - ev.clientX;
	current_view_pos.y += mousedown_pos.y - ev.clientY;
	if(current_view_pos.x < 0)
	    current_view_pos.x = 0;
	if(current_view_pos.y < 0)
	    current_view_pos.y = 0;
	if(current_view_pos.x > width)
	    current_view_pos.x = width;
	if(current_view_pos.y > height)
	    current_view_pos.y = height;

	this.style.left = -current_view_pos.x + "px";
	this.style.top = -current_view_pos.y + "px";
	
	mousedown_pos = undefined;
	this.style.cursor = "-moz-grab";
    }


    function getFloorPlanImgMap(zoom_index)
    {
	var imgmap = document.createElement("map");
	imgmap.name = bldgId + "_map";
	imgmap.id = bldgId + "_map";


	var zoom_factor = FLOOR_PLAN_ZOOM_LEVELS[zoom_index];

	for(var roomName in floorplancoords[bldgId])
	{
	    for(var r in floorplancoords[bldgId][roomName])
	    {
		
		var rectCoords = [];
		for(var i in floorplancoords[bldgId][roomName][r])
		{
		    rectCoords[i] = floorplancoords[bldgId][roomName][r][i] * zoom_factor;
		    rectCoords[i] = parseInt(rectCoords[i]);
		}
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
        $('#roomlist').load('/get_room/'+roomIdByName[name][String(roomName)]);/*
	    alert("Here you would see information about room id: "
		  + roomIdByName[name][String(roomName)] + "(" + name + " " + roomName + ")");*/
	}
	return area;
    }


    function resizeFloorPlan(old_zoom_index, new_zoom_index)
    {
	var img = document.getElementById("floorplan_img");
	var old_map = document.getElementById(bldgId + "_map");
	var old_zoom_factor = FLOOR_PLAN_ZOOM_LEVELS[old_zoom_index];
	var new_zoom_factor = FLOOR_PLAN_ZOOM_LEVELS[new_zoom_index];

	img.style.width = floorplancoordsWidth * new_zoom_factor + "px";

	// Remove old image map.
	old_map.parentNode.removeChild(old_map);

	// Recenter
	current_view_pos.x = current_view_pos.x * new_zoom_factor / old_zoom_factor;
	current_view_pos.y = current_view_pos.y * new_zoom_factor / old_zoom_factor;
	img.style.left = -current_view_pos.x + "px";
	img.style.top = -current_view_pos.y + "px";

	// Now create a new image map.
	getFloorPlanImgMap(new_zoom_index);
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
	    map_canvas.style.display = "block";
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
		resizeFloorPlan(current_zoom, current_zoom + 1);
		current_zoom++;
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
		resizeFloorPlan(current_zoom, current_zoom - 1);
		current_zoom--;
	    }
	}
	return button;
    }

    function getFloorUpButton()
    {
	var button = document.createElement("span");
	button.innerHTML = "^ floor up";
	button.id = "fp_floorup_button";
	button.className = "fp_button";

	button.onclick = function()
	{
	    displayFloorPlan(name, floor+1);
	}

	return button;
    }

    function getFloorDownButton()
    {
	var button = document.createElement("span");
	button.innerHTML = "V floor down";
	button.id = "fp_floordown_button";
	button.className = "fp_button";

	button.onclick = function()
	{
	    displayFloorPlan(name, floor-1);
	}

	return button;
    }

}