jtl = {};
function timelineInit(idTl, idInput) {
	//static references
	jtl.tl = document.getElementById(idTl);
	jtl.$tl = $('#'+idTl);
	
	//static constants
	jtl.wkdays = ['Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa'];
	
	jtl.minEndPadding = 12;
	jtl.minDayPadding = 6;
	jtl.minIntervalHt = 3; //including border
	jtl.maxIntervalHt = 100; //including border
	jtl.dayBorderHt = 3;  //between days

	jtl.minTickHt = 8;  //including border
	jtl.minLabelHt = 16; //time labels on left of timeline
	
	loadEvents();
	loadTimeline();
	addEvents();
}


/***************************************/
/* Timeline builders */
/***************************************/

/* Update base globals with params in filter input boxes */
function getTimelineParams() {
	var startDate = $('#jtl-startDay').val().split('/');
	jtl.startDate = new Date();
	clearDateTime(jtl.startDate);
	jtl.startDate.setFullYear(startDate[2]);
	jtl.startDate.setMonth(startDate[0]);
	jtl.startDate.setDate(startDate[1]);
	clearDateTime(jtl.startDate);
	jtl.nDays = $('#jtl-nDays').val();
	var startTime = $('#jtl-startTime').val().split(':');
	jtl.startIndex = timeToIndex(startTime[0], startTime[1]);
	var endTime = $('#jtl-endTime').val().split(':');
	jtl.endIndex = timeToIndex(endTime[0], endTime[1]);
}


function minRangeOfTimes() {
	return Math.ceil(((jtl.tl.offsetHt - 2*jtl.minEndPadding)/jtl.nDays - jtl.minDayPadding) / jtl.minIntervalHt);
}
function maxRangeOfTimes() {
	return Math.floor(((jtl.tl.offsetHt - 2*jtl.minEndPadding)/jtl.nDays - jtl.minDayPadding) / jtl.maxIntervalHt);
}

/* Load the timeline from scratch, used at init */
function loadTimeline() {
	removeTimeTicks();
	getTimelineParams();
	
	//compute the sizes of each day, each tick, given the parameters + timeline size
	jtl.nIntervals = jtl.endIndex - jtl.startIndex;
	var maxDayHt = Math.floor((jtl.tl.offsetHeight - 2*jtl.minEndPadding)/jtl.nDays) - jtl.dayBorderHt;
	var minDayPadding = (jtl.nIntervals==48?0:jtl.minDayPadding);
	var maxTicksHt = maxDayHt - 2*minDayPadding;
	jtl.intervalHt = Math.floor(maxTicksHt/(jtl.nIntervals-1)); //based on 1 interval per tick

	jtl.dayPadding = minDayPadding;
	jtl.dayHt = jtl.intervalHt*(jtl.nIntervals-1) + 2*jtl.dayPadding;
	jtl.endPadding = Math.floor((jtl.tl.offsetHeight - (jtl.dayHt + jtl.dayBorderHt)*jtl.nDays)/2);
	
	/*
	
	if (intervalHt >= jtl.minTickHt) {
		jtl.intervalsPerTick = 1;
		jtl.tickHt = Math.floor(intervalHt);
	} else {
		jtl.intervalsPerTick = Math.ceil(jtl.minTickHt/intervalHt/2)*2;
		jtl.tickHt = Math.floor(intervalHt*jtl.intervalsPerTick);
	}
	
	jtl.nTicks = Math.floor(jtl.nIntervals/jtl.intervalsPerTick);
	jtl.dayPadding = minDayPadding;
	jtl.intervalHt = Math.floor(intervalHt);
	jtl.dayHt = jtl.tickHt*(jtl.nTicks-1) + 2*jtl.dayPadding;
	jtl.endPadding = Math.floor((jtl.tl.offsetHeight - (jtl.dayHt + jtl.dayBorderHt)*jtl.nDays)/2);
	
	jtl.nTicksPerLabel = Math.ceil(jtl.minTimeHt/(jtl.tickHt+1));
	*/
	
	
	
	/*
		
	
	jtl.nTicks = jtl.endIndex - jtl.startIndex;
	var tickHt = dayHt/jtl.nTicks - 1;
	if (tickHt < jtl.minTickHt) {
		jtl.ticksPerMark = Math.ceil((jtl.minTickHt+1)/(tickHt+1));
		jtl.tickHt = Math.floor((tickHt+1)*jtl.ticksPerMark-1);
	} else {
		jtl.ticksPerMark = 1;
		jtl.tickHt = Math.floor(tickHt);
	}
	jtl.dayHt = Math.ceil((jtl.tickHt+1)*(jtl.nTicks/jtl.ticksPerMark+2));
	jtl.endMargin = (jtl.tl.offsetHeight - jtl.dayHt*jtl.nDays)/2;
	*/
	
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
		
		//+(jtl.dayPadding!=0&&i+jtl.intervalsPerTick>=jtl.nIntervals?'jtl-tick-last':'')
		var dHtSinceTick = jtl.minTickHt;
		var dHtSinceLabel = jtl.minLabelHt;
		
		for (var i=jtl.startIndex; i<jtl.endIndex; i++) {
			//calculate whether or not this interval has a border/label
			var hasBorder = false;
			var hasLabel = false;
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
			
			
			/*
		for (var i=0; i<jtl.nIntervals; i+=jtl.intervalsPerTick) {
			var divTick = document.createElement('div');
			divTick.setAttribute('class', 'jtl-tick '+(jtl.dayPadding==0&&i==0?'jtl-tick-first':'jtl-tick-border'));
			divTick.setAttribute('id', indexToId(d,i+jtl.startIndex));
			divTick.setAttribute('style', 'height:'+(jtl.tickHt-1)+'px;');
			divTicks.appendChild(divTick);
			
			if ((i/jtl.intervalsPerTick % jtl.nTicksPerLabel) == 0) {
				var divTime = document.createElement('div');
				divTime.setAttribute('class', 'jtl-time');
				$(divTime).html(indexToTime(i+jtl.startIndex));
				divTick.appendChild(divTime);
			}
		}*/
	}
}

function removeTimeTicks() {
	var c = jtl.tl;
	if (c.hasChildNodes())
		while (c.childNodes.length >= 1)
			c.removeChild(c.firstChild);	
}


/***************************************/
/* Event adders */
/***************************************/

function loadEvents() {
	
}

function addEvents() {
	for (id in jtl.events) {
		//need clearDateTime() on startTime
		var startTime = jtl.events[id].startTime;
		var startDayIndex = dateToDayIndex(date);
		if (startDayIndex < 0 || startDayIndex > jtl.nDays)
			continue;
		var startIndex = timeToIndex(startTime.getHour(), startTime.getMinute());
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

function clearDateTime(d) {
	d.setHours(0);d.setMinutes(0);d.setSeconds(0);d.setMilliseconds(0);
}
function timeToIndex(hour, min) {
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












function cmpDates(d1,d2) {
	if (d1.getFullYear() < d2.getFullYear()) return -1;
	else if (d1.getFullYear() > d2.getFullYear()) return 1;
	if (d1.getMonth() < d2.getMonth()) return -1;
	else if (d1.getMonth() > d2.getMonth()) return 1;
	if (d1.getDate() < d2.getDate()) return -1;
	else if (d1.getDate() > d2.getDate()) return 1;
	return 0;
}