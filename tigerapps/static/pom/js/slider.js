//This contains all the code to make the slider work.

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

function sliderInit() {
	weekday = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
	
    $( "#jmap-slider" ).slider({
        range: true,
        min: 0,
        max: 500,
        values: [0, 500],
        slide: function( event, ui ) {
            jevent.sliderLeftDate = convertToDate(ui.values[0]);
            $( "#slider-left-value" ).val(printDateTime(jevent.sliderLeftDate));
            
            jevent.sliderRightDate = convertToDate(ui.values[1]);
            $( "#slider-right-value" ).val(printDateTime(jevent.sliderRightDate));
        },
        
        stop: function (event, ui) {
        	if (oldLeft != ui.values[0] || oldRight != ui.values[1]) {
        		var get_params = datesToFilter(jevent.sliderLeftDate, jevent.sliderRightDate);
        		bldgsForFilter(get_params);
            	oldLeft = ui.values[0];
            	oldRight = ui.values[1];
            }
        }
    
    
    });
    oldLeft = 0;
    oldRight = 500;
    
    jevent.sliderLeftDate = convertToDate($( "#jmap-slider" ).slider( "values", 0 ));
    $( "#slider-left-value" ).val(printDateTime(jevent.sliderLeftDate));

    jevent.sliderRightDate = convertToDate($( "#jmap-slider" ).slider( "values", 1 ));
    $( "#slider-right-value" ).val(printDateTime(jevent.sliderRightDate));
} 
