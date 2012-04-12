
//PMAP - This file defines the "pmap" JS object which holds data for
//the Princeton University Campus Map app, as well as some
//functions used by the main application page.

//Copyright 2010 The Trustees of Princeton University

//Author: Kevin Perry, Educational Technology Centers, OIT, Princeton Univ.
//Sept, 2010

var pmap = {
		
	// Starting position info.
	start: {},
	
	// Building group lists
	listkeys: [],
	lists: {},
	
	// Main status flag.
	status: {},
	
	// Data timestamps.
	timestamp: {data: 0, map: 0},
	
	// Image tile loader status flags and vars.
	load: {loading: [], waiting: [], waiter: null, wait: 50},
	
	// Global list of organizations.
	orgs: {},

	// Stuff for the mouse-drag event handling.
	dragConnection: null,
	move: { x: 0, y: 0},

	// Global list of buildings.
	bldgs: new Array()
};
///////////////////////////////////////////////////

//CONFIGURATION

pmap.conf = {

	// The folder in which map image tiles are stored.
	tileDir: 'http://etcweb.princeton.edu/pumapdata/tiles',

	// The folder in which building images are stored.
	imageDir: 'http://etcweb.princeton.edu/pumapdata/images',

	// Data file names.
	//bldgsFile: 'http://etcweb.princeton.edu/pumapdata/locations.json',
	bldgsFile: 'http://etcweb.princeton.edu/mobile/map/json.php',

	// These should reflect the geocode coords of the map image.
	// I computed these from the image using Wyman House & 116 Prospect Ave
	latMin:  40.3158151,
	lonMin: -74.6712778,
	latMax:  40.3590167,
	lonMax: -74.5965600,

	// These define the size of the map display in pixels.
	divW: 700,
	divH: 620,

	// What zoom level to start at.
	startLevel: -1,

	// Where in the image to start, in Lat/Lon. (Currently near Art Museum)
	startCenterLat:  40.3470,
	startCenterLon: -74.6572,

	// building to highlight at start (or 0 for no init highlight)
	initHighlight: 1,
	initCenterHighlight: false,

	// Default radius to allow click from centroid of a bldg (at full rez.)
	defaultClickRadius: 80,

	// Default radius of a building highlight (at full rez.)
	defaultRadius: 50,

	// Minimum radius we will allow a building highlight to be (at full rez.)
	minRadius: 20,

	// Thickness of the box-border to draw for the highlight
	highlightThickness: 6,

	// Image to use when building has no photo
	noPhoto: 'nophoto.jpg'
};
///////////////////////////////////////////////////

//Un-needed, but interesting.
//var feetPerDegreeLatitude = 365228;

//Initialize dependent config params.
pmap.conf.lonDelta = pmap.conf.lonMax-pmap.conf.lonMin;
pmap.conf.latDelta = pmap.conf.latMax-pmap.conf.latMin;

function reportError(where, msg) {
	console.log(where+': '+msg);
	hide('imgdiv');
	hide('controls');
	dojo.create('p', {className: 'error', innerHTML: 'Sorry, the map is not available at  this time, due to technical problems.'}, 'infodiv');
	show('infodiv');
	dojo.xhrPost({
		url: 'err.php',
		content: { msg: where+': '+msg }
	});
}

function setStart() {
	if ( pmap.conf.startLevel == "max" ) {
		pmap.conf.startLevel = pmap.tileinfo.maxLevel;
	}
	if ( pmap.conf.startLevel > pmap.tileinfo.maxLevel ) {
		reportError('setStart', 'startLevel is too large');
	}
	if ( pmap.conf.startLevel < 0 ) {
		pmap.conf.startLevel += pmap.tileinfo.maxLevel;
	}
	if ( pmap.conf.startLevel < 0 ) {
		reportError('setStart', 'startLevel is too small');
	}
	var startX = (pmap.tileinfo.width*(pmap.conf.startCenterLon-pmap.conf.lonMin)/(pmap.conf.lonMax-pmap.conf.lonMin));
	var startY = (pmap.tileinfo.height*(pmap.conf.latMax-pmap.conf.startCenterLat)/(pmap.conf.latMax-pmap.conf.latMin));
	pmap.start.mag = Math.pow(pmap.tileinfo.magStep, (pmap.conf.startLevel-pmap.tileinfo.maxLevel));
	pmap.start.w = Math.round(pmap.tileinfo.width*pmap.start.mag);
	pmap.start.h = Math.round(pmap.tileinfo.height*pmap.start.mag);
	pmap.start.left = Math.round(pmap.conf.divW/2 - startX*pmap.start.mag);
	pmap.start.top = Math.round(pmap.conf.divH/2 - startY*pmap.start.mag);

	pmap.cur = {
		w: pmap.start.w,
		h: pmap.start.h,
		left: pmap.start.left,
		top: pmap.start.top,
		mag: pmap.start.mag,
		level: pmap.conf.startLevel
	};

	dojo.style('imgdiv', {
		width: pmap.conf.divW + 'px',
		height: pmap.conf.divH + 'px',
		maxWidth: pmap.conf.divW + 'px',
		maxHeight: pmap.conf.divH + 'px'
	});

	dojo.style('infodiv', {
		height: pmap.conf.divH + 'px'
	});
}

function loadBldgs() {
	dojo.xhrPost({
		url: pmap.conf.bldgsFile,
		content: { t: pmap.timestamp.data },
		handleAs: 'json',
		load: function(data) {
			if ( !data || !data.location ) {
				console.log('bad building data file!');
			}
			pmap.bldgs = data.location;
			pmap.timestamp.data = data.timestamp;
			afterDataLoad();
		},
		error: function(e) {
			console.log('failed to return bldg data: '+e);
			hide('imgdiv');
			hide('controls');
			dojo.create('p', {className: 'error', innerHTML: 'Sorry, the map is not available at  this time, due to technical problems.'}, 'infodiv');
			show('infodiv');
			dojo.xhrPost({
				url: 'err.php',
				content: { msg: 'data load: '+e }
			});
		}
	});
}

function loadTiles() {
	dojo.xhrPost({
		url: pmap.conf.tileDir+'/tiles.json',
		content: { t: pmap.timestamp.map },
		handleAs: 'json',
		load: function(data) {
			if ( !data || !data.width ) {
				console.log('bad tile data file!');
			}
			pmap.tileinfo = data;
			afterTileLoad();
		},
		error: function(e) {
			console.log('failed to return tile data: '+e);
			hide('imgdiv');
			hide('controls');
			dojo.create('p', {className: 'error', innerHTML: 'Sorry, the map is not available at  this time, due to technical problems.'}, 'infodiv');
			show('infodiv');
			dojo.xhrPost({
				url: 'err.php',
				content: { msg: 'tile load: '+e }
			});
		}
	});
}

function afterDataLoad() {
	if ( ! pmap.status.bldgsLoaded ) {

		pmap.status.bldgsLoaded = true;

		pmap.bldgById = {};
		
		var lastup = dojo.byId('lastupdated');
		if ( lastup ) {
			var dtlastup = new Date(Math.max(pmap.timestamp.data, pmap.timestamp.map)*1000);
			dojo.attr(lastup, 'innerHTML', 'last updated '+dtlastup.toLocaleDateString());
		}

		dojo.forEach(pmap.bldgs, function(entry) {
			pmap.bldgById[entry.location_code] = entry;
			if ( pmap.lists[entry.group] == null ) {
				pmap.listkeys.push(entry.group);
				pmap.lists[entry.group] = [];
			}
			pmap.lists[entry.group].push(entry);
			entry.organizations.sort(function(a, b){
				return ((a.name>b.name)?1:((a.name < b.name)?-1:0));
			});
			dojo.forEach(entry.organizations, function(org) {
				org.location_code = this.location_code;
				if ( pmap.lists[org.category] == null ) {
					pmap.listkeys.push(org.category);
					pmap.lists[org.category] = [];
				}
				pmap.lists[org.category].push(org);
				if ( org.category == 'Academic' || org.category == 'Administrative' ) {
					var deptkey = 'Department';
					if ( pmap.lists[deptkey] == null ) {
						pmap.listkeys.push(deptkey);
						pmap.lists[deptkey] = [];
					}
					pmap.lists[deptkey].push(org);
				}
			}, entry);
		});

		dojo.forEach(pmap.listkeys, function(key) {
			pmap.lists[key].sort(function(a, b){
				return ((a.name>b.name)?1:((a.name < b.name)?-1:0));
			});
		});

		loadCategory('Building');
	}
}

function afterTileLoad() {
	if ( pmap.status.bldgsLoaded &&
			! pmap.status.tilesLoaded ) {

		pmap.status.tilesLoaded = true;
		pmap.tiles = {};

		setStart();
		edgeDetect();
		setPosition();

		if ( pmap.conf.initHighlight > 0 ) {
			var initbldg = pmap.bldgById[pmap.conf.initHighlight];
			if ( initbldg ) {
				if ( pmap.conf.initCenterHighlight ) {
					centerAndShowBldg(initbldg);
				} else {
					showBldgInfo(initbldg);
					highlight(initbldg);
				}
			}
		}

		// Apply initial hash setting, if exists.
		if ( document.location.hash ) {
			var id = document.location.hash.substring(1);
			var bldg = lookup(id);
			if ( bldg ) {
				centerAndShowBldg(bldg);
			}
		}

	} else {
		setTimeout(afterTileLoad, 50);
	}
}

function startup() {

	// Not ready for this yet.
	// pmap.conf.isMobile = ( dojo.style('mflag', 'zIndex') == 1 );
	pmap.conf.isMobile = false;

	loadBldgs();
	loadTiles();
	otherSetup();
}

function otherSetup() {
	pmap.status.finalSetup = true;

	// "unselectable"-ness for IE.
	dojo.forEach(dojo.query('.unselectable'), function(obj) {
		obj.onselectstart = function() { return false; }
	});

	// Make sure we have a "hashchange" event driver.
	if ( ! document.onhashchange ) {
		pmap.currentHash = document.location.hash;
		setInterval(checkHashChange, 200);
	}

	// Set up the hashchange event handler.
	document.onhashchange = function() {
		var id = document.location.hash.substring(1);
		var bldg = lookup(id);
		if ( bldg ) {
			showBldgInfo(bldg);
			if ( moveBldgOnscreen(bldg) ) { moveToBldg(bldg); }
			highlight(bldg);
		} else {
			unhighlight();
		}
		return false;
	};

	mouseSetup();
}

function mouseSetup() {
	var obj = dojo.byId('imgdiv');

	dojo.connect(obj, 'onmousedown', obj, function (e) {
		e.preventDefault();
		pmap.move.x0 = e.clientX;
		pmap.move.y0 = e.clientY;
		pmap.move.x = e.clientX;
		pmap.move.y = e.clientY;
		pmap.status.clicking = true;
		disableDrag();
		pmap.dragConnection = dojo.connect(window.document, 'onmousemove', doDrag);
	});

	dojo.connect(window.document, 'onmouseup', obj, function (e) {
		e.preventDefault();
		disableDrag();
		if ( pmap.status.clicking ) {
			clickMe(e);
			pmap.status.clicking = false;
		}
	});
}

function checkHashChange() {
	if ( document.location.hash != pmap.currentHash ) {
		pmap.currentHash = document.location.hash;
		document.onhashchange();
	}
}

function disableDrag() {
	if ( pmap.dragConnection != null ) {
		dojo.disconnect(pmap.dragConnection);
		pmap.dragConnection = null;
	}
}

function setPosition() {
	dojo.style('theImage', {
		width: pmap.cur.w + 'px',
		height: pmap.cur.h + 'px',
		left: pmap.cur.left + 'px',
		top: pmap.cur.top + 'px'
	});
	loadImages();
}

function zoomin() {
	if ( pmap.cur.level < pmap.tileinfo.maxLevel ) {
		var oldmag = pmap.cur.mag;
		pmap.cur.level++;
		pmap.cur.mag = Math.pow(pmap.tileinfo.magStep, (pmap.cur.level - pmap.tileinfo.maxLevel));

		pmap.cur.w = Math.round(pmap.tileinfo.width*pmap.cur.mag);
		pmap.cur.h = Math.round(pmap.tileinfo.height*pmap.cur.mag);

		pmap.cur.left = Math.round((pmap.cur.left - pmap.conf.divW/2)*pmap.cur.mag/oldmag + pmap.conf.divW/2);
		pmap.cur.top = Math.round((pmap.cur.top - pmap.conf.divH/2)*pmap.cur.mag/oldmag + pmap.conf.divH/2);

		moveBldgOnscreen(pmap.highlitBldg);
		highlight(pmap.highlitBldg);

		hideAllImages();
		setPosition();
	} else {
		//alert('at max zoom already');
	}
}

function moveBldgOnscreen(bldg) {
	if ( bldg && checkBounds(bldg.geocode) ) {
		var a = lon2x(bldg.geocode.lon);
		var b = lat2y(bldg.geocode.lat);
		var r = getHighlightRadius(bldg) + pmap.conf.highlightThickness;
		var moved = false;
		if ( a < r ) {
			pmap.cur.left += Math.round(r - a);
			moved = true;
		} else if ( a > pmap.conf.divW - r ) {
			pmap.cur.left -= Math.round(a + r - pmap.conf.divW);
			moved = true;
		}
		if ( b < r ) {
			pmap.cur.top += Math.round(r - b);
			moved = true;
		} else if ( b > pmap.conf.divH - r ) {
			pmap.cur.top -= Math.round(b + r - pmap.conf.divH);
			moved = true;
		}
	}
	if ( moved ) {
		edgeDetect();
	}
	return moved;
}

function zoomout() {
	if ( pmap.cur.level > 0
			&& ( pmap.cur.w > pmap.conf.divW || pmap.cur.h > pmap.conf.divH ) ) {

		var oldmag = pmap.cur.mag;
		pmap.cur.level--;
		pmap.cur.mag = Math.pow(pmap.tileinfo.magStep, (pmap.cur.level - pmap.tileinfo.maxLevel));

		pmap.cur.w = Math.round(pmap.tileinfo.width*pmap.cur.mag);
		pmap.cur.h = Math.round(pmap.tileinfo.height*pmap.cur.mag);
		pmap.cur.left = Math.round((pmap.cur.left - pmap.conf.divW/2)*pmap.cur.mag/oldmag + pmap.conf.divW/2);
		pmap.cur.top = Math.round((pmap.cur.top - pmap.conf.divH/2)*pmap.cur.mag/oldmag + pmap.conf.divH/2);

		edgeDetect();

		highlight(pmap.highlitBldg);

		hideAllImages();
		setPosition();
	} else {
		//alert('at min zoom already');
	}
}

function doDrag(event) {
	event.preventDefault();
	if ( (pmap.move.x0-event.clientX)*(pmap.move.x0-event.clientX)
			+ (pmap.move.y0-event.clientY)*(pmap.move.y0-event.clientY) > 25 ) {
		pmap.move.x0 = -1000;
		pmap.move.y0 = -1000;
	} else {
		return;
	}
	pmap.cur.left -= (pmap.move.x-event.clientX);
	pmap.cur.top -= (pmap.move.y-event.clientY);
	highlight(pmap.highlitBldg);
	edgeDetect();
	pmap.move.x = event.clientX;
	pmap.move.y = event.clientY;
	setPosition();
	pmap.status.clicking = false;
}

function edgeDetect() {
	var moved = false;
	if ( pmap.cur.left > 0 ) {
		if ( pmap.cur.w <= pmap.conf.divW ) {
			pmap.cur.left = Math.round((pmap.conf.divW-pmap.cur.w)/2);
		} else {
			pmap.cur.left = 0;
		}
		moved = true;
	} else if ( pmap.cur.left + pmap.cur.w < pmap.conf.divW ) {
		if ( pmap.cur.w <= pmap.conf.divW ) {
			pmap.cur.left = Math.round((pmap.conf.divW-pmap.cur.w)/2);
		} else {
			pmap.cur.left = pmap.conf.divW - pmap.cur.w;
		}
		moved = true;
	}
	if ( pmap.cur.top > 0 ) {
		if ( pmap.cur.h <= pmap.conf.divH ) {
			pmap.cur.top = Math.round((pmap.conf.divH-pmap.cur.h)/2);
		} else {
			pmap.cur.top = 0;
		}
		moved = true;
	} else if ( pmap.cur.top + pmap.cur.h < pmap.conf.divH ) {
		if ( pmap.cur.h <= pmap.conf.divH ) {
			pmap.cur.top = Math.round((pmap.conf.divH-pmap.cur.h)/2);
		} else {
			pmap.cur.top = Math.round(pmap.conf.divH - pmap.cur.h);
		}
		moved = true;
	}
	if ( moved ) {
		highlight(pmap.highlitBldg);
	}
}

function clickMe(event) {
	var nearest = { dist: 9999, bldg: null };
	dojo.forEach(pmap.bldgs, function(entry) {
		var d = calcDist(entry, event);
		var r = pmap.conf.highlightThickness + pmap.cur.mag *
		((entry.radius>0) ? entry.radius : pmap.conf.defaultClickRadius);
		if ( d < r && r < this.dist ) {
			this.dist = r;
			this.bldg = entry;
		}
	}, nearest);
	if ( nearest.bldg != null ) {
		if ( document.location.hash != '#'+nearest.bldg.location_code ) {
			unhighlight();
			document.location.hash = nearest.bldg.location_code;
		}
	} else {
		unhighlight();
		document.location.hash = '';
	}
}

function showBldgInfo(bldg) {
	unhighlight();
	var info = dojo.byId('infodiv');
	dojo.attr(info, 'innerHTML', '');
	if ( ! bldg.image_url ) {
		bldg.image_url = pmap.conf.noPhoto;
	}
	dojo.create('img', {
		src: bldg.image_url,
		className: 'bldgimg',
		alt: '[Image of '+bldg.name+']'
	}, 
	dojo.create('div', { id: 'bldgimgdiv' }, info));
	info = dojo.create('div', {id: 'infotext'}, info);
	dojo.create('h2', {
		innerHTML: bldg.name
	}, info);
	dojo.forEach(bldg.organizations, function(org) {
		var line = dojo.create('li', {}, this.parent);
		if ( org.url ) {
			dojo.create('a', {
				href: org.url,
				className: 'orglink',
				innerHTML: org.name
			}, line);
		} else {
			dojo.create('span', {innerHTML: org.name}, line);
		}
		if ( org.phone ) {
			dojo.create('br', {}, line);
			dojo.create('span', {className: 'phone', innerHTML: org.phone}, line);
		}
	}, { parent: dojo.create('ul', {id: 'orgs'}, info) } );

	document.title = 'Campus Map - ' + bldg.name;

	if ( pmap.conf.isMobile ) {
		dojo.create('a', {innerHTML: 'View map', onclick: function(e){
			hide('infodiv');
			show('imgdiv');
		}}, info);
		hide('imgdiv');
		show('infodiv');
	}
}

function calcDist(entry, event) {
	var divpos = dojo.position('imgdiv', true);
	var a = lon2x(entry.geocode.lon) - event.pageX + divpos.x;
	var b = lat2y(entry.geocode.lat) - event.pageY + divpos.y;
	return Math.max(Math.abs(a), Math.abs(b));
}

function lat2y(ll) {
	var pct = (pmap.conf.latMax-ll)/pmap.conf.latDelta;
	return pct*pmap.cur.h + pmap.cur.top;
}

function lon2x(ll) {
	var pct = (ll-pmap.conf.lonMin)/pmap.conf.lonDelta;
	return pct*pmap.cur.w + pmap.cur.left;
}

function selCategory() {
	var sel = dojo.byId('categlist');
	var id = sel.options[sel.selectedIndex].value;
	loadCategory(id);
	unhighlight();
}

function loadCategory(id) {
	var parent = dojo.byId('bldglist');
	parent.innerHTML = '';
	dojo.create('option', {
		innerHTML: "",
		value: "",
		selected: "selected"
	}, parent);
	dojo.forEach(pmap.lists[id], function(entry) {
		var opt = dojo.create('option', {
			innerHTML: entry.name,
			value: entry.location_code
		}, this.parent);
	}, { parent: parent });
}

function selBldg() {
	var sel = dojo.byId('bldglist');
	var id = sel.options[sel.selectedIndex].value;
	if ( id > 0 ) {
		document.location.hash = id;
	} else {
		document.location.hash = '';
	}
}

function centerAndShowBldgById(id) {
	centerAndShowBldg(lookup(id));
}

function centerAndShowBldg(bldg) {
	if ( bldg ) {
		showBldgInfo(bldg);
		moveToBldg(bldg);
	} else {
		unhighlight();
	}
}

function lookup(id) {
	return pmap.bldgById[id];
}

function moveToBldg(bldg) {
	if ( bldg && checkBounds(bldg.geocode) ) {
		pmap.cur.left += Math.round(pmap.conf.divW/2 - lon2x(bldg.geocode.lon));
		pmap.cur.top += Math.round(pmap.conf.divH/2 - lat2y(bldg.geocode.lat));
		edgeDetect();
		setPosition();
		highlight(bldg);
	}
}

function highlight(bldg) {
	if ( bldg && checkBounds(bldg.geocode) ) {
		var r = getHighlightRadius(bldg);
		var rb = r + pmap.conf.highlightThickness;
		dojo.style('highlight', {
			borderWidth: pmap.conf.highlightThickness + 'px',
			left: Math.round(lon2x(bldg.geocode.lon) - rb) + 'px',
			top: Math.round(lat2y(bldg.geocode.lat) - rb) + 'px',
			width: Math.round(2*r) + 'px',
			height: Math.round(2*r) + 'px',
			display: 'inline'
		});
		pmap.highlitBldg = bldg;
	}
}

function checkBounds(geocode) {
	return ( geocode.lat > pmap.conf.latMin
			&& geocode.lat < pmap.conf.latMax
			&& geocode.lon > pmap.conf.lonMin
			&& geocode.lon < pmap.conf.lonMax
	);
}

function unhighlight() {
	hide('highlight');
	pmap.highlitBldg = null;
	dojo.attr('infodiv', 'innerHTML', '');
	document.title = 'Campus Map - Princeton University';
}

function getHighlightRadius(bldg) {
	return pmap.cur.mag*(
			(bldg.radius>pmap.conf.minRadius) ? bldg.radius
					: (bldg.radius>0) ? pmap.conf.minRadius
							: pmap.conf.defaultRadius
	);
}

function loadImages() {
	abortLoads();
	mainload(pmap.cur.level, true);
	show(pmap.tiles[pmap.cur.level].div);
}

function hideAllImages() {
	for ( var j = 0; j <= pmap.tileinfo.maxLevel; j++ ) {
		var levelSet = pmap.tiles[j];
		if ( levelSet != null ) {
			hide(levelSet.div);
		}
	}
}

function mainload(level, more) {
	var myLeft = levelLeft(level);
	var myTop = levelTop(level);
	var x1 = Math.floor(-myLeft/pmap.tileinfo.tilesize);
	var y1 = Math.floor(-myTop/pmap.tileinfo.tilesize);
	var x2 = Math.floor((pmap.conf.divW-myLeft)/pmap.tileinfo.tilesize);
	var y2 = Math.floor((pmap.conf.divH-myTop)/pmap.tileinfo.tilesize);
	for ( var j = x1; j <= x2; j++ ) {
		for ( var k = y1; k <= y2; k++ ) {
			loadImage(level, j, k);
		}
	}
	if ( more ) {
		pmap.load.waiting.push('loadMore('+level+','+x1+','+x2+','+y1+','+y2+');');
		pmap.load.waiting.push('mainload('+(level+1)+');');
		pmap.load.waiting.push('mainload('+(level-1)+');');
		// maybe we didn't make any calls to loadImage() above...
		while ( pmap.load.waiting.length >0 && ! pmap.load.waiter ) {
			eval(pmap.load.waiting.shift());
		}
	}
}

function abortLoads() {
	clearTimeout(pmap.load.waiter);
	pmap.load.waiter = null;
	pmap.load.waiting = [];
	pmap.load.loading = [];
	pmap.load.scans = 0;
}

function loadMore(level, x1, x2, y1, y2) {
	var j;
	for ( j = y1-1; j <= y2+1; j++ ) {
		loadImage(level, x1-1, j);
		loadImage(level, x2+1, j);
	}
	for ( j = x1; j <= x2; j++ ) {
		loadImage(level, j, y1-1);
		loadImage(level, j, y2+1);
	}
}

function levelLeft(level) {
	var dmag = Math.pow(pmap.tileinfo.magStep, (level - pmap.cur.level));
	return (pmap.cur.left - pmap.conf.divW/2)*dmag + pmap.conf.divW/2;
}

function levelTop(level) {
	var dmag = Math.pow(pmap.tileinfo.magStep, (level - pmap.cur.level));
	return (pmap.cur.top - pmap.conf.divH/2)*dmag + pmap.conf.divH/2;
}

function loadImage(level, xx, yy) {
	if ( level < 0 || level > pmap.tileinfo.maxLevel ) {
		return;
	}
	var levelMag = Math.pow(pmap.tileinfo.magStep, (level-pmap.tileinfo.maxLevel));
	var tilesW = pmap.tileinfo.width*levelMag/pmap.tileinfo.tilesize;
	var tilesH = pmap.tileinfo.height*levelMag/pmap.tileinfo.tilesize;
	if ( xx < 0 || xx >= tilesW || yy < 0 || yy >= tilesH ) {
		return;
	}
	var levelSet = pmap.tiles[level];
	if ( levelSet == null ) {
		pmap.tiles[level] = {
				rows: [],
				div: dojo.create('div', {
					style: {
						display: 'none',
						position: 'relative',
						width: Math.round(pmap.tileinfo.width*levelMag) + 'px',
						height: Math.round(pmap.tileinfo.height*levelMag) + 'px'
					}
				}, 'theImage')
		};
		levelSet = pmap.tiles[level];
	}
	var imgname = pmap.conf.tileDir+'/'+level+'-'+xx+'-'+yy+'.jpg?t='+pmap.timestamp.map;
	var rowSet = levelSet.rows[yy];
	if ( rowSet == null ) {
		levelSet.rows[yy] = {};
		rowSet = levelSet.rows[yy];
	}
	if ( rowSet[xx] == null ) {
		rowSet[xx] = dojo.create('img', {
			style: {
				position: 'absolute',
				left: pmap.tileinfo.tilesize*xx + 'px',
				top: pmap.tileinfo.tilesize*yy + 'px'
			}
		}, levelSet.div);
		pmap.load.loading.push(rowSet[xx]);
		if ( ! pmap.load.waiter ) {
			pmap.load.waiter = setTimeout(loadWait, pmap.load.wait);
		}
		// Do I need this, or is 'complete' OK?
		dojo.connect(rowSet[xx], 'load', rowSet[xx], function() {
			this.pmapready = true;
		});
		dojo.connect(rowSet[xx], 'error', rowSet[xx], function() {
			this.pmapready = true;
		});
		rowSet[xx].src = imgname;
	}
}

function loadWait() {
	pmap.load.scans++;
	pmap.load.waiter = true;
	if ( dojo.every(pmap.load.loading, function(e){return e.pmapready;}) ) {
		// All loading img's are ready.  Load next batch.
		pmap.load.loading = [];
		pmap.load.waiter = null;
		pmap.load.scans = 0;
		if ( pmap.load.waiting.length > 0 ) {
			eval(pmap.load.waiting.shift());
		}
	} else {
		pmap.load.waiter = setTimeout(loadWait, pmap.load.wait);
	}
}

function about() {
	show('about');
}

function show(obj) {
	dojo.style(obj, {display: 'block'});
}

function hide(obj) {
	dojo.style(obj, {display: 'none'});
}

