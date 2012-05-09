//MAP: Sets up all functionality related to events triggered by interactions
//with the map, including map scroll + tile/building loading, building
//click, and zoom (future)

//EVENTS: Sets up all functionality related to making ajax calls to the
//server for filtering events + loading events in the info box
//NOTE: should be loaded before map.js

jmap = {};
jevent = {};
function mapInit() {
	//links
	jmap.cursorGrabbing = 'url(/static/pom/img/closedhand.cur)';
	jmap.tilesDir = '/static/pom/img/tiles/';
	jmap.bldgsDir = '/static/pom/img/bldgs/';
	jmap.bldgsFile = '/static/pom/js/bldgs.json';
	jmap.bldgsDefaultSrc = '.png';
	jmap.bldgsHoverSrc = '-h.png';
	jmap.bldgsEventSrc = '-e.png';
	jmap.bldgsEventHoverSrc = '-eh.png';
	
	//static references
	jmap.mapContainer = document.getElementById('jmap-container');
	jmap.map = document.getElementById('jmap-movable');
	jmap.mapInfo = document.getElementById('jmap-info');
	jmap.infoTop = document.getElementById('info-top');

	//static constants
	jmap.tileSZ = 256; //square
	//jmap.mapBounds = {x1:68,y1:55,x2:2816,y2:2048};
	jmap.mapBounds = {x1:77,y1:55,x2:2715,y2:2046};
	
	//for dragging
	jmap.isDragging = false;
	jmap.mouseStart = null;
	jmap.mapStart   = null;
	jmap.objId		= null;

	//variables for loading tiles and buildings
	jmap.zoom = 4; 			//0=out,4=in
	var start = mapCenterToDisp(1300,560);
	jmap.dispX = start.x;	//displacement from the top-left
	jmap.dispY = start.y;
	jmap.map.style.left = -jmap.dispX;
	jmap.map.style.top = -jmap.dispY;
	loadBldgsJSON();
	jmap.loadedTiles = {};
	jmap.loadedBldgs = {};
	jevent.bldgCodeHasEvent = {};

	//now setup the drag + load the tiles/buildings
	setupGlobalDrag();
	window.onresize = loadTiles;
	loadTiles();
	
	/***/
	
	//links
	jevent.urlBldgsForFilter = '/bldgs/filter/';
	jevent.urlEventsForBldg = '/events/bldg/';
	jevent.urlEventsForAll = '/events/all/';
	jevent.urlBldgNames = '/bldgs/name/';
	
	jevent.htmlLoading = '<table style="margin:auto;height:24px;"><tr>' +
		'<td style="padding:1px 4px 0;">Loading...</td>' +
		'<td style="vertical-align:top;"><img src="/static/pom/img/loading_spinner.gif" height="20" width="20"/></td></tr></table>';

	jevent.bldgDisplayed = null;
	jevent.infoSize = 0; //0=not extended, 1=loading, 2=full extension
	jevent.filterType = -1; //events=0, hours=1, menus=2, laundry=3, printers=4
    jevent.eventLeftDate = convertToDate($( "#events-slider" ).slider( "values", 0 ));
    jevent.eventRightDate = convertToDate($( "#events-slider" ).slider( "values", 1 ));
	
	setupFilterTabs();
	setupActualFilters();
}


/***************************************/
/* General conversion tools */
/***************************************/

//ensures x,y input are within the bounds of the map
function boundDispX(x) {
	return -Math.max(Math.min(x, -jmap.mapBounds.x1), jmap.mapContainer.offsetWidth-jmap.mapBounds.x2);
}
function boundDispY(y) {
	return -Math.max(Math.min(y, -jmap.mapBounds.y1), jmap.mapContainer.offsetHeight-jmap.mapBounds.y2);
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

function bldgIdToCode(id) {
	return id.split("-")[1];
}
function bldgCodeToId(bldgCode) {
	return jmap.zoom+"-"+bldgCode;
}

//building position is 1:1 in zoom level 4
//function objIndexToPos(index) {}


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
	
	/* For getting building coordinates using mouse on map
	$(window).keydown(function(event) {
		if (event.ctrlKey && event.keyCode == 49) {
			event.preventDefault();
			$('#box3').val($('#box1').val());
			$('#box4').val($('#box2').val());
			$('#box7').val($('#box5').val()-$('#box3').val());
			$('#box8').val($('#box6').val()-$('#box4').val());
		}
		if (event.ctrlKey && event.keyCode == 50) {
			event.preventDefault();
			$('#box5').val($('#box1').val());
			$('#box6').val($('#box2').val());
			$('#box7').val($('#box5').val()-$('#box3').val());
			$('#box8').val($('#box6').val()-$('#box4').val());
		}
	})
	*/
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
	var mapOffset = $(domEle).offset();
	var mapContainerOffset = $('#jmap-container').offset();
	jmap.mapStart = {x:mapOffset.left-mapContainerOffset.left, y:mapOffset.top-mapContainerOffset.top};
}
// erases that junk
function recordMouseUp() {
	document.body.style.cursor = 'default';
	jmap.isDragging = false;
	jmap.mouseStart = null;
	jmap.mapStart   = null;
	loadTiles();
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

		//it's actually noticeably slower if we load for every drag
		//loadTiles();
	}
	/* For getting building coordinates using mouse on map
	var c = mouseCoords(ev);
	var mapContainerOffset = $('#jmap-container').offset();
	$('#box1').val(jmap.dispX+c.x+mapContainerOffset.left);
	$('#box2').val(jmap.dispY+c.y+mapContainerOffset.top);
	*/
}

//Returns the current coordinates of the mouse
function mouseCoords(ev){
	if(ev.pageX || ev.pageY)
		return {x:ev.pageX, y:ev.pageY};
	return {
		x:ev.clientX+document.body.scrollLeft-document.body.clientLeft,
		y:ev.clientY+document.body.scrollTop-document.body.clientTop
	};	
}



/***************************************/
/* For tile loading function of map */
/***************************************/

// load and set up drag for tiles that are on the current view screen
function loadTiles() {
	var tileBounds = tilesOnMap();
	//alert(tileBounds.minX+','+tileBounds.maxX+';'+tileBounds.minY+','+tileBounds.maxY);
	for (x=tileBounds.minX; x<=tileBounds.maxX; x++) {
		for (y=tileBounds.minY; y<=tileBounds.maxY; y++) {
			var id = tileIndexToId(x,y);
			if (jmap.loadedTiles[id] == undefined) {
				var domEle = document.createElement('img');
				jmap.loadedTiles[id] = domEle;
				domEle.setAttribute('src', jmap.tilesDir+id+'.png');
				domEle.setAttribute('class', 'jmap-tile');
				domEle.setAttribute('id', id);
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
		maxX: Math.ceil(Math.min(jmap.mapBounds.x2, jmap.dispX+jmap.mapContainer.offsetWidth) / jmap.tileSZ)-1,
		maxY: Math.ceil(Math.min(jmap.mapBounds.y2, jmap.dispY+jmap.mapContainer.offsetHeight) / jmap.tileSZ)-1
	};
}


/***************************************/
/* For bldg loading function of map */
/***************************************/

//load the bldgs.json file that holds all HTML-element data for the buildings
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

// load and set up hover/click for buildings that are on the loaded tile identified by 'id'
function loadTileBldgs(id) {
	var bldgsOnTile = jmap.bldgsTile[id];
	if (bldgsOnTile == undefined) return;
	for (index in bldgsOnTile) {
		var id = bldgsOnTile[index];
		if (jmap.loadedBldgs[id] == undefined) {
			var bldg = jmap.bldgsInfo[id];
			var domEle = document.createElement('img');
			jmap.loadedBldgs[id] = {'domEle':domEle};
			domEle.setAttribute('class', 'jmap-bldg');
			domEle.setAttribute('id', id);
			domEle.setAttribute('style', 'z-index:'+bldg.zIndex+';');
			setupBldg(domEle);
			domEle.style.height = bldg.height;
			domEle.style.width = bldg.width;
			domEle.style.left = bldg.left;
			domEle.style.top = bldg.top;
			domEle.onmousedown = function(ev){recordMouseDown(ev, jmap.map);};
			domEle.ondragstart = function(ev){ev.preventDefault();};
			jmap.map.appendChild(domEle);
		}
	}
}

function setupBldg(domEle) {
	if (jevent.bldgCodeHasEvent[bldgIdToCode(domEle.id)]) {
		if (!jmap.loadedBldgs[domEle.id].event)
			setupEventBldg(domEle);
	} else {
		if (jmap.loadedBldgs[domEle.id].event || jmap.loadedBldgs[domEle.id].event == undefined)
			setupPlainBldg(domEle);
	}
}
function setupPlainBldg(domEle) {
	domEle.setAttribute('src', jmap.bldgsDir+domEle.id+jmap.bldgsDefaultSrc);
	domEle.onmouseover = function(ev){domEle.src=jmap.bldgsDir+domEle.id+jmap.bldgsHoverSrc;};
	domEle.onmouseout  = function(ev){domEle.src=jmap.bldgsDir+domEle.id+jmap.bldgsDefaultSrc;};
	domEle.onclick = function(ev){};
	jmap.loadedBldgs[domEle.id].event = false;
}
function setupEventBldg(domEle) {
	domEle.setAttribute('src', jmap.bldgsDir+domEle.id+jmap.bldgsEventSrc);
	domEle.onmouseover = function(ev){domEle.src=jmap.bldgsDir+domEle.id+jmap.bldgsEventHoverSrc;};
	domEle.onmouseout  = function(ev){domEle.src=jmap.bldgsDir+domEle.id+jmap.bldgsEventSrc;};
	domEle.onclick = function(ev){handleBldgClick(ev,domEle);};
	jmap.loadedBldgs[domEle.id].event = true;
}
function handleBldgClick(ev,domEle) {
	var bldgCode = bldgIdToCode(domEle.id);
	if (jevent.bldgDisplayed == bldgCode) {
		/* hide the building info if building clicked is the one that's shown */
		hideInfoEvent();
	} else
		/* otherwise, load the clicked building */
		AJAXeventsForBldg(bldgCode);
}



/***************************************************************************/
/***************************************************************************/
/***************************************************************************/

/***************************************/
/* For parsing the filter options into GET request parameters */
/***************************************/

/* These setup the filters so that AJAX calls are sent when the filters are changed */
function setupFilterTabs() {
	$("#info-top-types input").click(function(ev) {
		handleFilterTypeChange(ev.target.value);
	});
	$("#other-info-types input").click(function(ev) {
		var newFilterType = ev.target.value;
		if (jevent.filterType != newFilterType) {
			jevent.filterType = newFilterType;
			if (newFilterType < 5) //only <5 is implemented in Django
				handleFilterChange();
		}
	});
	handleFilterTypeChange(0);
}
/* Called when the events/hours/menus/etc tabs are clicked. Changes the filters
 * displayed + loads bldgs for filter + reloads events for filter if events already open */
function handleFilterTypeChange(newFilterType) {
	if (jevent.filterType != newFilterType) {
		jevent.filterType = newFilterType;
		$(".top-tab").css('display', 'none');
		$("#top-tab-"+newFilterType).css('display', 'block');
		$(".bot-options").hide();
		$("#bot-options-"+newFilterType).show();
		if (newFilterType < 5) //only <5 is implemented in Django
			AJAXbldgsForFilter();
		if (jevent.bldgDisplayed != null)
			hideInfoEvent();
	}
}
function handleFilterChange() {
	AJAXbldgsForFilter();
	if (jevent.bldgDisplayed != null)
		AJAXeventsForBldg(jevent.bldgDisplayed);
		AJAXeventsForAll();
}

/* These return the GET params that should be sent in every AJAX call */
function getFilterParams() {
	var get_params = {type: jevent.filterType};
	if (jevent.filterType == 0) {
		//get dates from slider if searching events
		$.extend(get_params, datesToFilter(jevent.eventLeftDate, jevent.eventRightDate));
	}
	return get_params;
}
function datesToFilter(startDate, endDate) {
	return {
		m0: startDate.getMonth()+1,
		d0: startDate.getDate(),
		y0: startDate.getFullYear(),
		h0: startDate.getHours(),
		m1: endDate.getMonth()+1,
		d1: endDate.getDate(),
		y1: endDate.getFullYear(),
		h1: endDate.getHours()
	}
}

/***************************************/
/* For lighting up the correct buildings */
/***************************************/

function AJAXbldgsForFilter() {
	showMapLoading();
	$.ajax(jevent.urlBldgsForFilter, {
		data: getFilterParams(),
		dataType: 'json',
		success: displayFilteredBldgs,
		error: function(jqXHR, textStatus, errorThrown) {
			hideMapLoading();
			handleAjaxError(jqXHR, textStatus, errorThrown);
		}
	});
}

/* Success callback for AJAXbldgsForFilter */
function displayFilteredBldgs(data) {
	hideMapLoading();
	for (bldgCode in jevent.bldgCodeHasEvent)
		jevent.bldgCodeHasEvent[bldgCode] = false;
	for (i in data.bldgs)
		jevent.bldgCodeHasEvent[data.bldgs[i]] = true;
	for (id in jmap.loadedBldgs)
		setupBldg(jmap.loadedBldgs[id].domEle);
}


function showMapLoading() {
	var domEle = document.createElement('div');
	domEle.setAttribute('id','map-loading');
	domEle.setAttribute('class','map-box');
	domEle.innerHTML = jevent.htmlLoading;
	jmap.mapContainer.appendChild(domEle);
}
function hideMapLoading() {
	jmap.mapContainer.removeChild(document.getElementById('map-loading'));
}




/***************************************/
/* For rendering data in the info box */ 
/***************************************/

function AJAXeventsForAll() {
	displayInfoLoading();
	$.ajax(jevent.urlEventsForAll, {
		data: getFilterParams(),
		dataType: 'json',
		success: displayInfoEvent,
		error: function(jqXHR, textStatus, errorThrown) {
			hideInfoEvent();
			handleAjaxError(jqXHR, textStatus, errorThrown);
		}
	});
}

function AJAXeventsForBldg(bldgCode) {
	displayInfoLoading();
	$.ajax(jevent.urlEventsForBldg+bldgCode, {
		data: getFilterParams(),
		dataType: 'json',
		success: displayInfoEvent,
		error: function(jqXHR, textStatus, errorThrown) {
			hideInfoEvent();
			handleAjaxError(jqXHR, textStatus, errorThrown);
		}
	});
}

/* Success callback for AJAXeventsForBldg */
function displayInfoEvent(data) {
	if (data.error != null) {
		hideInfoEvent();
		alert(data.error);
	} else {
		$('#info-bot').html(data.html);
		jevent.bldgDisplayed = data.bldgCode;
		if (jevent.infoSize != 2) {
			/* Expand the info box if it's not already expanded */
			jevent.infoSize = 2;
			$('#info-bot').css('overflow-y', 'scroll');
			$('#info-divider').css('border-top', '1px solid #C0C0C0');
			$('#info-bot').animate({
				height: jmap.mapInfo.offsetHeight-jmap.infoTop.offsetHeight-80 + 'px',
			}, 400);
		}
	}
}

function displayInfoLoading() {
	$('#info-bot').css('overflow-y', 'hidden');
	$('#info-divider').css('border-top', '1px solid #C0C0C0');
	$('#info-bot').html(jevent.htmlLoading);
	if (jevent.infoSize == 0) {
		/* Expand the info box to loading size if it's not expanded at all */
		jevent.infoSize = 1;
		$('#info-bot').animate({
			height:'23px',
		}, 100);
	}
}

function hideInfoEvent() {
	jevent.infoSize = 0;
	jevent.bldgDisplayed = null;
	$('#info-divider').css('border-style','none');
	$('#info-bot').animate({
		height:'0px',
	}, 200);
}





/***************************************/
/* Predefined filters                  */ 
/***************************************/
function setupActualFilters() {
	locationFilter();
}

//load the bldgs.json file that holds all HTML-element data for the buildings
function locationFilter() {
	$.ajax(jevent.urlBldgNames, {		
		dataType: 'json',
		success: function(data) {
			jevent.bldgNames = data;
			
			// create list of building names
			var nameList = new Array();
			var i = 0;
			for (name in data)
				nameList[i++] = name;
			
			$( "#location-search" ).autocomplete({
				source: nameList, 
				delay: 0,
				minLength: 3,
			});
		},
		error: handleAjaxError
	});
	
	$('#location-search-form').submit(function(event) {
		// get submitted building's code, center map on it, and display it's events
		bldgName = $('#location-search').val();
		bldgCode = jevent.bldgNames[bldgName];
		centerOnBldg(bldgCode);
		return false;
	});
}


function centerOnBldg(bldgCode) {
	// calculate new center coords
	var bldgID = bldgCodeToId(bldgCode);
	var bldgObject = jmap.bldgsInfo[bldgID];
	var centroidX = bldgObject.left + bldgObject.width/2;
	var centroidY = bldgObject.top + bldgObject.height/2;
	centroid = mapCenterToDisp(centroidX, centroidY);
	
	// jump to this location, refresh tiles
	jmap.dispX = centroid.x;	
	jmap.dispY = centroid.y;
	$(jmap.map).animate({
		left: -jmap.dispX,
		top: -jmap.dispY,
	}, {
		duration: 100,
		complete: loadTiles
	});
}





