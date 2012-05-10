/***************************************/
/* jqueryui setup */
/***************************************/

function utilInit() {
	jDisplay = {};
	
	$("input:submit").button();
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
        values: [20, 40],
        slide: function( event, ui ) {
        	//sliderLeftTimeVal and sliderRightTimeVal will contain arrays where the zeroth 
        	//element is the hour (0-23) and the first element is the minutes (0 or 30)
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
		width:'535px'
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

function eventEntryMouseover(domEle) {
	var eventId = jtlFn.htmlIdToEventId(domEle.id);
	var eventEntry = document.getElementById('event-entry-'+eventId);
	var tlMark = document.getElementById('jtl-mark-'+eventId);
	var bldgDict = jmap.loadedBldgs[bldgCodeToId(jevent.eventsData[eventId])];
	eventEntry.style.background='#ECECEC';
	tlMark.style.background='#E9692C';
	if (bldgDict != undefined) 	$(bldgDict.domEle).mouseover();
}
function eventEntryMouseout(domEle) {
	var eventId = jtlFn.htmlIdToEventId(domEle.id);
	var eventEntry = document.getElementById('event-entry-'+eventId);
	var tlMark = document.getElementById('jtl-mark-'+eventId);
	var bldgDict = jmap.loadedBldgs[bldgCodeToId(jevent.eventsData[eventId])];
	//jevent.eventsJson
	eventEntry.style.background='white';
	tlMark.style.background='orange';
	if (bldgDict != undefined) 	$(bldgDict.domEle).mouseout();
}
function eventEntryClick(domEle) { //only for the timeline
	var eventId = jtlFn.htmlIdToEventId(domEle.id);
	var infoBot = $('#info-bot');
	infoBot.animate({
        scrollTop: $("#event-entry-"+eventId).position().top+infoBot.scrollTop()-infoBot.position().top-15
    }, 100);
}


function jExpand() {
	$('.jexpand-main').mouseover(function() {
		$(this).find('.jexpand-dots').hide();
		$(this).find('.jexpand-long').show();
	});
	$('.jexpand-main').mouseout(function() {
		$(this).find('.jexpand-dots').show();
		$(this).find('.jexpand-long').hide();
	});
}


/***************************************/
/* Utility functions */
/***************************************/

function clearDateTime(d) {
	d.setHours(0);d.setMinutes(0);d.setSeconds(0);d.setMilliseconds(0);
}

function handleAjaxError(jqXHR, textStatus, errorThrown) {
    if (confirm(errorThrown + ': Show error?')) {
        win = window.open();
        win.document.write(jqXHR.responseText);
    }
}

