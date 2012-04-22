
//PMAP - This file defines the "pmap" JS object which holds data for
//the Princeton University Campus Map app, as well as some
//functions used by the main application page.

var jmap = {};
function init() {
	//links
	jmap.cursorGrabbing = 'url(/static/pom/img/closedhand.cur)';
	jmap.tilesDir = '/static/pom/img/tiles/';
	jmap.bldgsDir = '/static/pom/img/bldgs/';
	jmap.bldgsFile = '/static/pom/js/bldgs.json';
	jmap.bldgsClick = '/bldg/';
	jmap.bldgsPlainSrc = '.jpg';
	jmap.bldgsHoverSrc = '-h.jpg';
	
	//static references
	jmap.mapContainer = document.getElementById('jmap-container');
	jmap.map = document.getElementById('jmap-movable');
	//jmap.$mapContainer = $('#jmap-container');
	
	//static constants
	jmap.tileSZ = 256; //square
	jmap.mapSZ = [{},{},{},{x:1024,y:1024,scale:2},{x:2816,y:2048,scale:1}];
	
	//for dragging
	jmap.isDragging = false;
	jmap.mouseStart = null;
	jmap.mapStart   = null;
	jmap.objId		= null;

	//for loading tiles
	jmap.zoom = 4; 			//0=out,4=in
	var start = mapCenterToDisp(900,900);
	jmap.dispX = start.x;	//displacement from the top-left
	jmap.dispY = start.y;
	jmap.map.style.left = -jmap.dispX;
	jmap.map.style.top = -jmap.dispY;
	

	loadBldgsJSON();
	jmap.loadedTiles = {};
	jmap.loadedBldgs = {};
	
	setupGlobalDrag();
	window.onresize = loadTiles;
	loadTiles();
}


/***************************************/
/* General conversion tools */
/***************************************/

//ensures x,y input are within the bounds of the map
function boundDispX(x) {
	return -Math.max(Math.min(x, 0), jmap.mapContainer.offsetWidth-jmap.mapSZ[jmap.zoom].x);
}
function boundDispY(y) {
	return -Math.max(Math.min(y, 0), jmap.mapContainer.offsetHeight-jmap.mapSZ[jmap.zoom].y);
}

//given a center coordinate, compute top-left coordinate (dispX/dispY)
function mapCenterToDisp(x,y) {
	return {
		x:boundDispX(jmap.mapContainer.offsetWidth/2-x),
		y:boundDispY(jmap.mapContainer.offsetHeight/2-y)
	};
}

//convert between tile index and HTML-id
function tileIndexToId(x,y) {
	return jmap.zoom+"-"+x+"-"+y;
}
function tileIdToIndex(id)  {
	var a=id.split('-');
	return {x:parseInt(a[1]),y:parseInt(a[2])};
}

//compute position of tile
function tileIdToPos(id) {
	var index = tileIdToIndex(id);
	return {
		left: index.x*jmap.tileSZ,
		top: index.y*jmap.tileSZ
	};
}

//building position is 1:1 in zoom level 4
//function objIndexToPos(index) {}


/***************************************/
/* For tile loading function of map */
/***************************************/

// load and set up drag for tiles that are on the current view screen
function loadTiles() {
	var tileBounds = tilesOnMap();
	//alert(tileBounds.minX+','+tileBounds.maxX+';'+tileBounds.minY+','+tileBounds.maxY);
	for (x=tileBounds.minX; x<=tileBounds.maxX; x++) {
		for (y=tileBounds.minY; y<=tileBounds.maxY; y++) {
			var id = tileIndexToId(y,x);
			if (jmap.loadedTiles[id] == undefined) {
				var domEle = document.createElement('img');
				jmap.loadedTiles[id] = domEle;
				domEle.setAttribute('src', jmap.tilesDir+id+'.jpg');
				domEle.setAttribute('class', 'jmap-tile');
				domEle.setAttribute('id', id);
				domEle.setAttribute('style', 'position:absolute;width:256px;height:256px;');
				var pos = tileIdToPos(id);
				domEle.style.left = pos.left;
				domEle.style.top = pos.top;
				jmap.map.appendChild(domEle);
				setupTileDrag(domEle);
				loadTileBldgs(id);
			}
		}
	}
	//jmap.tiles = $('.jmap-tile');
}

//return bounds on which tiles should be loaded right now, with edge checking
function tilesOnMap() {
	return {
		minX: Math.floor(jmap.dispX/jmap.tileSZ),
		minY: Math.floor(jmap.dispY/jmap.tileSZ),
		maxX: Math.ceil(Math.min(jmap.mapSZ[jmap.zoom].x, jmap.dispX+jmap.mapContainer.offsetWidth) / jmap.tileSZ)-1,
		maxY: Math.ceil(Math.min(jmap.mapSZ[jmap.zoom].y, jmap.dispY+jmap.mapContainer.offsetHeight) / jmap.tileSZ)-1
	};
}


/***************************************/
/* For bldg loading function of map */
/***************************************/

// load and set up hover/click for buildings that are on the loaded tile identified by 'id'
function loadTileBldgs(id) {
	var bldgsOnTile = jmap.bldgsTile[id];
	if (bldgsOnTile == undefined) return;
	for (index in bldgsOnTile) {
		var id = bldgsOnTile[index];
		if (jmap.loadedBldgs[id] == undefined) {
			var domEle = document.createElement('img');
			jmap.loadedBldgs[id] = domEle;
			domEle.setAttribute('src', jmap.bldgsDir+id+jmap.bldgsPlainSrc);
			domEle.setAttribute('class', 'jmap-bldg');
			domEle.setAttribute('id', id);
			domEle.setAttribute('style', 'position:absolute;');
			var bldg = jmap.bldgsInfo[id];
			domEle.style.height = bldg.height;
			domEle.style.width = bldg.width;
			domEle.style.left = bldg.left;
			domEle.style.top = bldg.top;
			jmap.map.appendChild(domEle);
			setupBldgClick(domEle);
		}
	}
}

// load the bldgs.json file that holds all HTML-element data for the buildings
function loadBldgsJSON() {
	$.ajax(jmap.bldgsFile, {
		async: false,
		dataType: 'json',
		success: function(data) {
			jmap.bldgsTile = data.bldgsTile;
			jmap.bldgsInfo = data.bldgsInfo;
		},
		error: handleAjaxError
	});
}

function setupBldgClick(domEle) {
	domEle.ondragstart = function(ev){ev.preventDefault();};
	domEle.onmouseover = function(ev){domEle.src=jmap.bldgsDir+domEle.id+jmap.bldgsHoverSrc;};
	domEle.onmouseout  = function(ev){domEle.src=jmap.bldgsDir+domEle.id+jmap.bldgsPlainSrc;};
	domEle.onclick = function(ev){handleBldgClick(ev,domEle);};
}

function handleBldgClick(ev,domEle) {
	$.ajax(jmap.bldgsClick+domEle.id, {
		success: function(data) {
			$('#info-bldgName').html(data);
		},
		error: handleAjaxError
	});
}


/***************************************/
/* For drag-scroll function of the map */
/* http://www.webreference.com/programming/javascript/mk/column2/index.html */
/***************************************/

// bind drag-setup to mousedown on the elements
// bind mouseover->drag to mousemove anywhere, if drag-setup
// bind drag-unsetup to mouseup anywhere
function setupGlobalDrag() {
	document.onmousemove = mouseMove;
	document.onmouseup = recordMouseUp
}
function setupTileDrag(domEle) {
	domEle.onmousedown = function(ev){recordMouseDown(ev, jmap.map);};
	domEle.ondragstart = function(ev){ev.preventDefault();};
}

// records where the mouse click-down happened
function recordMouseDown(ev, domEle) {
	document.body.style.cursor = jmap.cursorGrabbing;
	jmap.isDragging = true;
	jmap.mouseStart = mouseCoords(ev);
	var objOffset = $(domEle).offset();
	jmap.mapStart	= {x:objOffset.left, y:objOffset.top};
}
// erases that junk
function recordMouseUp() {
	document.body.style.cursor = 'default';
	jmap.isDragging = false;
	jmap.mouseStart = null;
	jmap.mapStart   = null;
	loadTiles();
	
	$('#box1x').val(jmap.map.style.left);
	$('#box1y').val(jmap.map.style.top);
}
// Moves the map if mouse is clicked down on the map
function mouseMove(ev){
	if (jmap.isDragging) {
		// find the mouse position
		ev           = ev || window.event;
		var mousePos = mouseCoords(ev);
		
		// move the map to the correct position
		var diffX = mousePos.x - jmap.mouseStart.x;
		var diffY = mousePos.y - jmap.mouseStart.y;
		jmap.dispX = boundDispX(jmap.mapStart.x+diffX);
		jmap.dispY = boundDispY(jmap.mapStart.y+diffY);
		jmap.map.style.left = -jmap.dispX;
		jmap.map.style.top  = -jmap.dispY;
		
		$('#box1x').val(jmap.map.style.left);
		$('#box1y').val(jmap.map.style.top);
	}
}

//Returns the current coordinates of the mouse
function mouseCoords(ev){
	if(ev.pageX || ev.pageY)
		return {x:ev.pageX, y:ev.pageY};
	return {
		x:ev.clientX + document.body.scrollLeft - document.body.clientLeft,
		y:ev.clientY + document.body.scrollTop  - document.body.clientTop
	};	
}


/***************************************/
/* Utility functions */
/***************************************/

function handleAjaxError(jqXHR, textStatus, errorThrown) {
	alert(errorThrown);
}



