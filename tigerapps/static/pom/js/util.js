/***************************************/
/* jqueryui setup */
/***************************************/

function utilInit() {
	$("input:submit").button();
	$("#info-top-types").buttonset();
	sliderInit();
}

function sliderInit() {
	weekday = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    oldLeft = -1;
    oldRight = -1;
    var sliderEle = $( "#events-slider" );
	
    sliderEle.slider({
        range: true,
        min: 0,
        max: 500,
        values: [0, 100],
        slide: function( event, ui ) {
            jevent.eventLeftDate = convertToDate(ui.values[0]);
            $( "#slider-left-value" ).val(printDateTime(jevent.eventLeftDate));
            
            jevent.eventRightDate = convertToDate(ui.values[1]);
            $( "#slider-right-value" ).val(printDateTime(jevent.eventRightDate));
        },
        
        stop: function (event, ui) {
        	if (oldLeft != ui.values[0] || oldRight != ui.values[1]) {
        		handleFilterChange();
            	oldLeft = ui.values[0];
            	oldRight = ui.values[1];
            }
        }
    });
    
    
    $( "#slider-left-value" ).val(printDateTime(convertToDate(sliderEle.slider( "values", 0 ))));
    $( "#slider-right-value" ).val(printDateTime(convertToDate(sliderEle.slider( "values", 1 ))));
}

function timeDelta(x) {
	return (1/(500*500.0)*(x*x))
}
function convertToDate(sliderVal) {
	var currentTime = new Date();
	var lastTime = new Date();
	lastTime.setTime(currentTime.getTime() + 2629743*1000*timeDelta(sliderVal));
    return (lastTime);
}
function printDateTime(dateObj) {
    var hours = dateObj.getHours();
    var am = true;
    if (hours > 12) {
       am = false;
       hours -= 12;
    } else if (hours == 12) {
       am = false;
    } else if (hours == 0) {
       hours = 12;
    }
    return weekday[dateObj.getDay()] + " " + (dateObj.getMonth()+1) + "/" +
    	dateObj.getDate() + "/" + dateObj.getFullYear() + ": " +
    	hours + (am ? "AM" : "PM");
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

/***************************************/
/* Utility functions */
/***************************************/

function jExpand() {
	$('.jexpand-main').mouseover(function() {
		$(this).find('.jexpand-longdesc').show(100);
	});
	$('.jexpand-main').mouseout(function() {
		$(this).find('.jexpand-longdesc').hide(100);
	});
}

function handleAjaxError(jqXHR, textStatus, errorThrown) {
    if (confirm(errorThrown + ': Show error?')) {
        win = window.open();
        win.document.write(jqXHR.responseText);
    }
}

