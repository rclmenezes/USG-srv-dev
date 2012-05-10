/*jTimeline - timeline object.
 * 
 * 
 * 
 */


jtl = {};
jtlFn = {};

//static constants
jtl.wkdays = ['Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa'];
jtl.minEndPadding = 12;
jtl.minDayPadding = 6;
jtl.minIntervalHt = 3; //including border
jtl.maxIntervalHt = 100; //including border
jtl.dayBorderHt = 3;  //between days
jtl.minTickHt = 8;  //including border
jtl.minLabelHt = 16; //time labels on left of timeline


/***************************************/
/* Intended for public */
/***************************************/

/* Display a JTL object in id */
function jTimeline(id, params) {
	//static references
	jtl.tl = document.getElementById(id);
	jtl.$tl = $(jtl.tl);
	
	//data from django
	jtl.events = {};

	jtl.tl.class = 'jtl-tl';
	jtlFn.buildTimeline(params);
}


/* NADER: Call this on slide in your hours slider, and return false if this is violated */
/* Allowed min/max range of the # of half-hours the timeline can handle. Depends on nDays */
jtlFn.minHoursRange = function() {
	return Math.ceil(((jtl.tl.offsetHt - 2*jtl.minEndPadding)/jtl.nDays - jtl.minDayPadding) / jtl.minIntervalHt);
}
jtlFn.maxHoursRange = function() {
	return Math.floor(((jtl.tl.offsetHt - 2*jtl.minEndPadding)/jtl.nDays - jtl.minDayPadding) / jtl.maxIntervalHt);
}


/***************************************/
/* Input builders */
/***************************************/

/* Update globals with params in filter input boxes */
jtlFn.loadParams = function(params) {
	jtl.startDate = params.startDate;
	jtl.nDays = params.nDays;
	jtl.startIndex = jtlFn.timeToIndex(params.startTime[0], params.startTime[1]);
	jtl.endIndex = jtlFn.timeToIndex(params.endTime[0], params.endTime[1]);
	jtl.nIntervals = jtl.endIndex - jtl.startIndex;
	if (jtl.nIntervals > jtlFn.maxHoursRange() || jtl.nIntervals < jtlFn.minHoursRange())
		return false;
	return true;
}



/***************************************/
/* Timeline builders */
/***************************************/

/* Load the timeline from scratch, used at init */
jtlFn.buildTimeline = function(params) {
	if (!jtlFn.loadParams(params)) {alert('bad params: range of hours too small');return;}
	jtlFn.clearTimeline();
	
	//compute the sizes of each day, each tick, given the parameters + timeline size
	var maxDayHt = Math.floor((jtl.tl.offsetHeight - 2*jtl.minEndPadding)/jtl.nDays) - jtl.dayBorderHt;
	var minDayPadding = (jtl.nIntervals==48?0:jtl.minDayPadding);
	var maxTicksHt = maxDayHt - 2*minDayPadding;
	jtl.intervalHt = Math.floor(maxTicksHt/(jtl.nIntervals-1)); //based on 1 interval per tick
	jtl.dayPadding = minDayPadding;
	jtl.dayHt = jtl.intervalHt*(jtl.nIntervals-1) + 2*jtl.dayPadding;
	jtl.endPadding = Math.floor((jtl.tl.offsetHeight - (jtl.dayHt + jtl.dayBorderHt)*jtl.nDays)/2);
	
	//for the day labels
	var tmpDate = new Date();
	tmpDate.setTime(jtl.startDate.getTime());
	
	for (var d=-1; d<=jtl.nDays; d++) {
		var divDay = document.createElement('div');
		divDay.setAttribute('class', 'jtl-day');
		divDay.setAttribute('style', 'height:'+jtl.dayHt+'px;top:'+((jtl.dayHt+jtl.dayBorderHt)*d+jtl.endPadding)+'px;');
		jtl.tl.appendChild(divDay);

		var divDate = document.createElement('div');
		divDate.setAttribute('class', 'jtl-date');
		divDate.setAttribute('style', 'width:'+jtl.dayHt+'px;top:'+((jtl.dayHt+jtl.dayBorderHt)/2-7)+'px;right:'+(-jtl.dayHt/2+7)+'px');
		tmpDate.setDate(jtl.startDate.getDate()+d);
		$(divDate).html(dateAbbrStr(tmpDate));
		divDay.appendChild(divDate);
		
		var divTicks = document.createElement('div');
		divTicks.setAttribute('class', 'jtl-tick-box');
		divTicks.setAttribute('style', 'height:100%;padding-top:'+jtl.dayPadding+'px;');
		divDay.appendChild(divTicks);
		
		var dHtSinceTick = jtl.minTickHt;
		var dHtSinceLabel = jtl.minLabelHt;
		
		for (var i=jtl.startIndex; i<jtl.endIndex; i++) {
			//calculate whether or not this interval has a border/label
			var hasBorder = false;
			var hasLabel = false;  //time label
			if (i%2==0 && dHtSinceTick >= jtl.minTickHt) { //if it's on the hour, and dHt is satisfied
				if (!(jtl.dayPadding==0 && i==jtl.startIndex))
					hasBorder = true;
				dHtSinceTick = 0; 
				if (dHtSinceLabel >= jtl.minLabelHt) {
					hasLabel = true;
					dHtSinceLabel = 0;
				}
			}
			dHtSinceTick += jtl.intervalHt;
			dHtSinceLabel += jtl.intervalHt;

			var divIntv = document.createElement('div');
			divIntv.setAttribute('class', 'jtl-tick '+(jtl.dayPadding==0&&i==jtl.startIndex?'jtl-tick-first':(hasBorder?'jtl-tick-border':'')));
			divIntv.setAttribute('id', indexToId(d,i));
			divIntv.setAttribute('style', 'height:'+(hasBorder?jtl.intervalHt-1:jtl.intervalHt)+'px;');
			divTicks.appendChild(divIntv);
			
			if (hasLabel) {
				var divLabel = document.createElement('div');
				divLabel.setAttribute('class', 'jtl-time');
				$(divLabel).html(indexToTime(i));
				divIntv.appendChild(divLabel);
			}
		}
	}
}

jtlFn.clearTimeline = function() {
	var c = jtl.tl;
	if (c.hasChildNodes())
		while (c.childNodes.length >= 1)
			c.removeChild(c.firstChild);	
}


/***************************************/
/* Event adders */
/***************************************/

jtlFn.addJTLEvents = function() {
	for (var id in jtl.events) {
		var startTime = jtl.events[id].startTime;
		var startDayIndex = dateToDayIndex(date);
		if (startDayIndex < 0 || startDayIndex > jtl.nDays)
			continue;
		var startIndex = jtlFn.timeToIndex(startTime.getHour(), startTime.getMinute());
		if (startIndex < jtl.startIndex && startIndex > jtl.endIndex)
			continue;
		var id = indexToId(startDayIndex, startIndex);
		var divTick = document.getElementById(id);
		var eventDot = document.createElement('div');
		eventDot.setAttribute('class', 'jtl-event');
		divTick.appendChild(eventDot);
	}
}



/***************************************/
/* Time conversions */
//could account for non :00/:30 later
/***************************************/

jtlFn.timeToIndex = function(hour, min) {
	return hour*2 + Math.round(min/30);
}
function dateToDayIndex(date) {
	return (date.getTime() - jtl.startDate.getTime())/86400000; 
}
// converts day + time index to id of div
function indexToId(day, ind) {
	return 'jtl-tick-'+day+'-'+ind;
}
/*function indexToDisp(ind) {
	if (ind < jtl.startIndex || ind > jtl.endIndex)
		return -1;
	return (ind-jtl.startIndex)/jtl.ticksPerMark*(jtl.tickHt+1)-7;
}*/
function indexToTime(ind) {
	var hour = Math.floor(ind/2);
	var ampm, min;
	if (hour < 12) {
		if (hour==0) hour = 12;
		ampm = 'a';
	} else {
		if (hour!=12) hour-=12;
		ampm = 'p';
	}
	if (ind%2)		min = '30';
	else			min = '00';
	return hour + ':' + min + ampm;
}

function dateAbbrStr(d) {
	return jtl.wkdays[d.getDay()] + ' ' + d.getMonth()+'/'+d.getDate()+'/'+d.getFullYear();
}


