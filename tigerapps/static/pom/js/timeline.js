jtl = {};
function timelineInit(id) {
	jtl.tl = document.getElementById(id);
	jtl.$tl = $('#'+id);
	
	jtl.tl.class = 'timeline';
	
}


function addTimeTicks() {
	
}




function setupDesign() {
	jtl.$tl.css('border','1px solid gray');
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
