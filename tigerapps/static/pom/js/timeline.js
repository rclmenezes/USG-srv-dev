jtl = {};
function timelineInit(idTl, idInput) {
	//static references
	jtl.tl = document.getElementById(idTl);
	jtl.$tl = $('#'+idTl);
	
	//static constants
	jtl.dayBorderHt = 2; //in addition to 1 border
	jtl.minTickHt = 7; //not including border
	jtl.wkdays = ['Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa'];
	
	dispTimeTicks();
}


/***************************************/
/* Timeline builders */
/***************************************/

function dispTimeTicks() {
	removeTimeTicks();
	getTimelineParams();
	
	/* compute the heights of each element */
	jtl.nTicks = jtl.endIndex - jtl.startIndex;
	var dayHt = Math.floor(jtl.tl.offsetHeight / jtl.nDays) - jtl.dayBorderHt;
	var tickHt = Math.floor(dayHt/(jtl.nTicks+1)) - 1;
	if (tickHt < jtl.minTickHt) {
		jtl.tickFactor = Math.ceil((jtl.minTickHt+1)/(tickHt+1));
		jtl.tickHt = (tickHt+1)*jtl.tickFactor-1;
	} else {
		jtl.tickFactor = 1;
		jtl.tickHt = tickHt;
	}
	jtl.dayHt = (jtl.tickHt+1)*(jtl.nTicks/jtl.tickFactor+1);
		
	
	var tmpDate = new Date();
	tmpDate.setTime(jtl.startDate.getTime());
		
	for (var d=0; d<jtl.nDays; d++) {
		var divDay = document.createElement('div');
		divDay.setAttribute('class', 'jtl-box jtl-day');
		divDay.setAttribute('style', 'height:'+jtl.dayHt+'px;top:'+((jtl.dayHt+jtl.dayBorderHt)*d)+'px');
		jtl.tl.appendChild(divDay);
		
		var divTicks = document.createElement('div');
		divTicks.setAttribute('class', 'jtl-tick-box'+(d!=jtl.nDays?' jtl-tick-box-border':''));
		divTicks.setAttribute('style', 'height:'+jtl.dayHt+'px;');
		divDay.appendChild(divTicks);
		
		var domEle = document.createElement('div');
		domEle.setAttribute('class', 'jtl-box jtl-date');
		domEle.setAttribute('style', 'width:'+jtl.dayHt+'px;top:'+(jtl.dayHt/2-7+jtl.dayBorderHt/2)+'px;right:'+(-jtl.dayHt/2+7)+'px');
		$(domEle).html(dateAbbrStr(tmpDate));
		tmpDate.setDate(tmpDate.getDate()+1);
		divDay.appendChild(domEle);

		for (i=0; i<jtl.nTicks; i+=jtl.tickFactor) {
			var domEle = document.createElement('hr');
			domEle.setAttribute('class', 'jtl-box jtl-tick');
			domEle.setAttribute('style', 'height:'+jtl.tickHt+'px');
			divTicks.appendChild(domEle);
		}
	}
}

function removeTimeTicks() {
	var c = jtl.tl;
	if (c.hasChildNodes())
		while (c.childNodes.length >= 1)
			c.removeChild(c.firstChild);	
}



/***************************************/
/* Time conversions */
//could account for non :00/:30 later
/***************************************/

function getTimelineParams() {
	var startDate = $('#jtl-startDay').val().split('/');
	jtl.startDate = new Date();
	jtl.startDate.setFullYear(startDate[2]);
	jtl.startDate.setMonth(startDate[0]);
	jtl.startDate.setDate(startDate[1]);
	jtl.nDays = $('#jtl-nDays').val();
	jtl.startIndex = timeToIndex($('#jtl-startTime').val());
	jtl.endIndex = timeToIndex($('#jtl-endTime').val());
}
function timeToIndex(str) {
	var s = str.split(':');
	return s[0]*2 + s[1]/30;
}
function indexToTime(ind) {
	var hour = ind/2;
	var ampm;
	if (hour > 12 || hour == 0)	ampm = 'AM';
	else						ampm = 'PM';
	return hour + ':' + (ind%2)*30 + ' ' + ampm;
}

function dateAbbrStr(d) {
	return jtl.wkdays[d.getDay()] + ' ' + d.getMonth()+'/'+d.getDate()+'/'+d.getFullYear();
}










