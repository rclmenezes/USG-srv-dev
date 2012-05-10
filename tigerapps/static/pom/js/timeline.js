/* jTimeline - timeline object.
 * Author: Josh Chen (joshchen@princeton.edu)
 * 
 * Initialize or reload by calling jTimeline().
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
jtl.tlWidth = 100;


/***************************************/
/* Intended for public */
/***************************************/

/* Display a JTL object in id */
function jTimeline(id, timelineParams, markData, fnMarkMouseover, fnMarkMouseout, fnMarkClick) {
	//static references
	jtl.tl = document.getElementById(id);
	jtl.$tl = $(jtl.tl);
	jtl.tl.class = 'jtl-tl';
	
	//data for loading marks
	jtl.markData = markData;
	jtl.fnMarkMouseover = fnMarkMouseover;
	jtl.fnMarkMouseout = fnMarkMouseout;
	jtl.fnMarkClick = fnMarkClick;

	jtlFn.buildTimeline(timelineParams);
}




/***************************************/
/* Input builders */
/***************************************/

/* Update globals with params in filter input boxes */
jtlFn.loadParams = function(params) {
	/* Allowed min/max range of the # of half-hours the timeline can handle. Depends on nDays */
	/*jtlFn.minHoursRange = function() {
		return Math.floor(((jtl.tl.offsetHeight - 2*jtl.minEndPadding)/jtl.nDays - jtl.minDayPadding) / jtl.maxIntervalHt);
	}
	jtlFn.maxHoursRange = function() {
		return Math.ceil(((jtl.tl.offsetHeight - 2*jtl.minEndPadding)/jtl.nDays - jtl.minDayPadding) / jtl.minIntervalHt);
	}*/
	jtl.startDate = params.startDate;
	jtl.nDays = parseInt(params.nDays);
	jtl.startIndex = jtlFn.timeToIndex(params.startTime[0], params.startTime[1]);
	jtl.endIndex = jtlFn.timeToIndex(params.endTime[0], params.endTime[1]);
	jtl.nIntervals = jtl.endIndex - jtl.startIndex;
	/*if (jtl.nIntervals > jtlFn.maxHoursRange() || jtl.nIntervals < jtlFn.minHoursRange())
		return false;
	return true;*/
}


/***************************************/
/* Timeline builders */
/***************************************/

/* Load the timeline from scratch, used at init */
jtlFn.buildTimeline = function(params) {
	//if (!jtlFn.loadParams(params)) {alert('jTl bad params: range of hours will cause timeline to display badly');return;}
	jtlFn.loadParams(params)
	jtlFn.clearTimeline();
	
	//compute the sizes of each day, each tick, given the parameters + timeline size
	var maxDayHt = Math.floor((jtl.tl.offsetHeight - 2*jtl.minEndPadding)/jtl.nDays) - jtl.dayBorderHt;
	var minDayPadding = (jtl.nIntervals==48?0:jtl.minDayPadding);
	var maxTicksHt = maxDayHt - 2*minDayPadding;
	jtl.intervalHt = Math.floor(maxTicksHt/jtl.nIntervals); //based on 1 interval per tick
	jtl.dayPadding = minDayPadding;
	jtl.dayHt = jtl.intervalHt*jtl.nIntervals + 2*jtl.dayPadding;
	jtl.endPadding = Math.floor((jtl.tl.offsetHeight - (jtl.dayHt + jtl.dayBorderHt)*jtl.nDays)/2);
	jtl.nEndDays = Math.ceil(jtl.endPadding*2 / jtl.dayHt);
	
	//for the day labels
	var tmpDate = new Date();
	tmpDate.setTime(jtl.startDate.getTime());
	
	for (var d=-jtl.nEndDays; d<jtl.nDays+jtl.nEndDays; d++) {
		var divDay = document.createElement('div');
		divDay.setAttribute('class', 'jtl-day');
		divDay.setAttribute('style', 'height:'+jtl.dayHt+'px;top:'+((jtl.dayHt+jtl.dayBorderHt)*d+jtl.endPadding)+'px;');
		jtl.tl.appendChild(divDay);

		var divDate = document.createElement('div');
		divDate.setAttribute('class', 'jtl-date');
		divDate.setAttribute('style', 'width:'+jtl.dayHt+'px;top:'+((jtl.dayHt+jtl.dayBorderHt)/2-7)+'px;right:'+(-jtl.dayHt/2+7)+'px');
		tmpDate.setDate(jtl.startDate.getDate()+d);
		$(divDate).html(jtlFn.dateAbbrStr(tmpDate));
		divDay.appendChild(divDate);
		
		var divTicks = document.createElement('div');
		divTicks.setAttribute('class', 'jtl-tick-box'+(d<0||d>=jtl.nDays?' jtl-tick-box-inactive':''));
		divTicks.setAttribute('style', 'height:'+(jtl.dayHt-jtl.dayPadding*2)+'px;padding:'+jtl.dayPadding+'px 0;');
		divDay.appendChild(divTicks);
		
		var dHtSinceTick = jtl.minTickHt;
		var dHtSinceLabel = jtl.minLabelHt;
		
		for (var i=jtl.startIndex; i<=jtl.endIndex; i++) {
			//calculate whether or not this interval has a border/label
			var hasBorder = false;
			var hasLabel = false;  //time label
			if (i%2==0 && dHtSinceTick >= jtl.minTickHt) { //if it's on the hour, and dHt is satisfied
				if (!(jtl.dayPadding==0 && (i==jtl.startIndex || i==jtl.endIndex)))
					hasBorder = true;
				dHtSinceTick = 0; 
				if (dHtSinceLabel >= jtl.minLabelHt) {
					if (!(jtl.dayPadding==0 && i==jtl.endIndex))
						hasLabel = true;
					dHtSinceLabel = 0;
				}
			}
			dHtSinceTick += jtl.intervalHt;
			dHtSinceLabel += jtl.intervalHt;

			var divIntv = document.createElement('div');
			divIntv.setAttribute('class', 'jtl-tick '+(jtl.dayPadding==0&&i==jtl.startIndex?'jtl-tick-first':(hasBorder?'jtl-tick-border':'')));
			divIntv.setAttribute('id', jtlFn.indexToId(d+'-'+i));
			divIntv.setAttribute('style', 'height:'+(hasBorder?jtl.intervalHt-1:jtl.intervalHt)+'px;');
			divTicks.appendChild(divIntv);
			
			if (hasLabel) {
				var divLabel = document.createElement('div');
				divLabel.setAttribute('class', 'jtl-time');
				$(divLabel).html(jtlFn.indexToTime(i));
				divIntv.appendChild(divLabel);
			}
		}
	}
	
	jtlFn.addJTLEvents()
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
	for (var tickIndex in jtl.markData) {
		var tickId = jtlFn.indexToId(tickIndex);
		var divTick = document.getElementById(tickId);
		console.log(tickId);
		var tickData = jtl.markData[tickIndex];
		var nMarks = tickData.length;
		
		for (var i in tickData) {
			var markData = tickData[i];
			var eventMark = document.createElement('div');
			eventMark.setAttribute('class', 'jtl-mark');
			eventMark.setAttribute('id', 'jtl-mark-'+markData['eventId']);
			eventMark.style.left = Math.round((parseInt(i)+.5)/nMarks * jtl.tlWidth)-3;
			eventMark.style.zIndex = 110+(i%2);
			//may want to add in if statements if this is to be a real library
			eventMark.onmouseover = function(ev){jtl.fnMarkMouseover(this);};
			eventMark.onmouseout = function(ev){jtl.fnMarkMouseout(this);};
			eventMark.onclick = function(ev){jtl.fnMarkClick(this);};
			divTick.appendChild(eventMark);
		}
	}
}



/***************************************/
/* Time conversions */
//could account for non :00/:30 later
/***************************************/

jtlFn.htmlIdToEventId = function(htmlId) {
	return htmlId.split('-')[2];
}

jtlFn.timeToIndex = function(hour, min) {
	return hour*2 + Math.round(min/30);
}
jtlFn.dateToDayIndex = function(date) {
	return (date.getTime() - jtl.startDate.getTime())/86400000; 
}
// converts day + time index to id of div
jtlFn.indexToId = function(ind) {
	return 'jtl-tick-'+ind;
}
jtlFn.indexToTime = function(ind) {
	var hour = Math.floor(ind/2);
	var ampm, min;
	hour = hour % 24;
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

jtlFn.dateAbbrStr = function(d) {
	return jtl.wkdays[d.getDay()] + ' ' + (1+d.getMonth())+'/'+d.getDate();//+'/'+d.getFullYear().toString().substring(2);
}


