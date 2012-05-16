/***************************************/
/* jqueryui setup */
/***************************************/

function displayInit() {
	jDisplay = {};
	
	$("input:submit").button();
	$(":button").button();
	$("#info-top-types").buttonset();
	
	//events inputs
	$("#jtl-startDate").datepicker();
	$("#jtl-startDate").datepicker('setDate', new Date());
	setupJTLSlider();
	
	//timeline display/toggle
	setupJTLDisplay();
}


/***************************************/
/* Inputs display */ 
/***************************************/

function setupJTLSlider() {
    oldLeft = -1;
    oldRight = -1;
    var sliderEle = $("#jtl-hours-slider");
	
    sliderEle.slider({
        range: true,
        min: 0,
        max: 48,
        values: [20, 40], //initial
        slide: function( event, ui ) {
        	//sliderLeftTimeVal and sliderRightTimeVal will contain arrays where the zeroth 
        	//element is the hour (0-23) and the first element is the minutes (0 or 30)
        	if (ui.values[1] - ui.values[0] < 4) return false;
        	var startTime = indexToTimeArr(ui.values[0]);
    		var endTime = indexToTimeArr(ui.values[1]);
            $("#jtl-slider-start").val(printTime(startTime));
            $("#jtl-slider-end").val(printTime(endTime));
        },
        
        stop: function (event, ui) {
        	if (oldLeft != ui.values[0] || oldRight != ui.values[1]) {
            	var startTime = indexToTimeArr(ui.values[0]);
        		var endTime = indexToTimeArr(ui.values[1]);
                $("#jtl-startTime").val(printTimeMilit(startTime));
                $("#jtl-endTime").val(printTimeMilit(endTime));
            	oldLeft = ui.values[0];
            	oldRight = ui.values[1];
            	
        		handleFilterChange();
            }
        }
    });

	var startTime = indexToTimeArr(sliderEle.slider( "values", 0 ));
	var endTime = indexToTimeArr(sliderEle.slider( "values", 1 ));
    $("#jtl-slider-start").val(printTime(startTime));
    $("#jtl-slider-end").val(printTime(endTime));
    $("#jtl-startTime").val(printTimeMilit(startTime));
    $("#jtl-endTime").val(printTimeMilit(endTime));
}

function indexToTimeArr(sliderVal) {
	return [Math.floor(sliderVal/2), (sliderVal%2)*30];
}
function printTimeMilit(timeArr) {
	return timeArr[0] + ':' + timeArr[1];
}
function printTime(timeArr) {
    var hours = timeArr[0];
    hours %= 24
    var am = true;
    if (hours > 12) {
       am = false;
       hours -= 12;
    } else if (hours == 12) {
       am = false;
    } else if (hours == 0) {
       hours = 12;
    }
    zeroPad = ''
    if (timeArr[1] == 0)
    	zeroPad += "0"
    return hours + ":" + timeArr[1] + zeroPad + ' ' + (am ? "AM" : "PM");
}



/***************************************/
/* Timeline display */ 
/***************************************/

function setupJTLDisplay() {
	jDisplay.timelineShown = true
	$('#jtl-toggle').click(function() {
		if (jDisplay.timelineShown)
			hideTimeline();
		else
			showTimeline();
	})
	showTimeline();
}
function displayTimeline() {
	if (jDisplay.timelineShown) showTimeline();
	$('#jtl-toggle').show();
}
function undisplayTimeline() {
	var tmp = jDisplay.timelineShown;
	$('#jtl-toggle').hide();
	hideTimeline();
	jDisplay.timelineShown = tmp;
}
function showTimeline() {
	$(jmap.jtl).show(80)
	$(jmap.info).animate({
		width:'540px'
	}, 80);
	$('#jtl-toggle span').attr('class', 'ui-icon ui-icon-carat-1-w');
	jDisplay.timelineShown = true;
}
function hideTimeline() {
	$(jmap.jtl).hide(80)
	$(jmap.info).animate({
		width:'380px'
	}, 80);
	$('#jtl-toggle span').attr('class', 'ui-icon ui-icon-carat-1-e');
	jDisplay.timelineShown = false;
}



/***************************************/
/* Mouseover/out functions */
/***************************************/

function eventEntryMouseover(eventId, fromBldg) {
	var eventEntry = document.getElementById('event-entry-'+eventId);
	var tlMark = document.getElementById('jtl-mark-'+eventId);
	var bldgDict = jmap.loadedBldgs[bldgCodeToId(jevent.eventsData[eventId].bldgCode)];
	eventEntry.style.background='#ECECEC';
	tlMark.setAttribute('class', 'jtl-mark-hover'); 
	tlMark.style.left = parseInt(tlMark.style.left, 10) - 1;
	//tlMark.style.background='#E56717';
	if (fromBldg != true) {
		$(tlMark).tipsy('show');
		if (bldgDict != undefined) eventBldgMouseoverColor(bldgDict.domEle);
	}
}
function eventEntryMouseout(eventId, fromBldg) {
	var eventEntry = document.getElementById('event-entry-'+eventId);
	var tlMark = document.getElementById('jtl-mark-'+eventId);
	var bldgDict = jmap.loadedBldgs[bldgCodeToId(jevent.eventsData[eventId].bldgCode)];
	eventEntry.style.background='white';
	tlMark.setAttribute('class', 'jtl-mark');
	tlMark.style.left = parseInt(tlMark.style.left, 10) + 1;
	//tlMark.style.background='orange';
	if (fromBldg != true) {
		$(tlMark).tipsy('hide');
		if (bldgDict != undefined) eventBldgMouseoutColor(bldgDict.domEle);
	}
}
function eventEntryClick(eventId, dontScroll) { //only for the timeline
	var eventEntry = document.getElementById('event-entry-'+eventId);
	var infoBot = $('#info-bot');
	if (dontScroll != true) {
		infoBot.animate({
	        scrollTop: $("#event-entry-"+eventId).position().top+infoBot.scrollTop()-infoBot.position().top-15
	    }, 300);
	}
	$(eventEntry).find('.info-event-dots').toggle();
	$(eventEntry).find('.info-event-long').toggle(300);
}
function eventBldgMouseover(domEle) {
	if (jevent.filterType == 0) {
		var bldgCode = bldgIdToCode(domEle.id);
		for (var eventid in jevent.eventsData) {
			if (jevent.eventsData[eventid].bldgCode == bldgCode)
				eventEntryMouseover(eventid, true);
		}
	}
}
function eventBldgMouseout(domEle) {
	if (jevent.filterType == 0) {
		var bldgCode = bldgIdToCode(domEle.id);
		for (var eventid in jevent.eventsData) {
			if (jevent.eventsData[eventid].bldgCode == bldgCode)
				eventEntryMouseout(eventid, true);
		}
	}
}

/***************************************/
/* Utility functions */
/***************************************/

function clearDateTime(d) {
	d.setHours(0);d.setMinutes(0);d.setSeconds(0);d.setMilliseconds(0);
}

function handleAjaxError(jqXHR, textStatus, errorThrown) {
	var e1 = 'Sorry! A server error occurred while you were browsing the page: "'+errorThrown+'".';
	var e2 = 'Please contact our team at it@princetonusg.com if you see this message again.';
    if (confirm(e1+'\n\n'+e2+'\n\nView error?')) {
        win = window.open();
        win.document.write(jqXHR.responseText);
    }
	$('#info-bot').html('<div class="info-error">'+e1+'<br/><br/>'+e2+'</div>');
}

