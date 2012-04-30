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

function sliderInit() {
	var weekday=new Array(7);
	weekday[0]="Sunday";
	weekday[1]="Monday";
	weekday[2]="Tuesday";
	weekday[3]="Wednesday";
	weekday[4]="Thursday";
	weekday[5]="Friday";
	weekday[6]="Saturday";
	
	
    $( "#jmap-slider" ).slider({
        range: true,
        min: 0,
        max: 500,
        values: [0, 500],
        slide: function( event, ui ) {
            sliderLeftDate = convertToDate(ui.values[0]);
            var hours = sliderLeftDate.getHours();
            var am = true;
            if (hours > 12) {
               am = false;
               hours -= 12;
            } if (hours == 12) {
               am = false;
            } if (hours == 0) {
               hours = 12;
            }
            $( "#slider-left-value" ).val(weekday[sliderLeftDate.getDay()] + " " + sliderLeftDate.getMonth() + "/" + sliderLeftDate.getDate() + "/" + sliderLeftDate.getFullYear() + ": " + hours + (am ? "AM" : "PM"));
            
            
            sliderRightDate = convertToDate(ui.values[1]);
            var hours = sliderRightDate.getHours();
            var am = true;
            if (hours > 12) {
               am = false;
               hours -= 12;
            } if (hours == 12) {
               am = false;
            } if (hours == 0) {
               hours = 12;
            }
            $( "#slider-right-value" ).val(weekday[sliderRightDate.getDay()] + " " + sliderRightDate.getMonth() + "/" + sliderRightDate.getDate() + "/" + sliderRightDate.getFullYear() + ": " + hours + (am ? "AM" : "PM"));
        }
    });
    
    sliderLeftDate = convertToDate($( "#jmap-slider" ).slider( "values", 0 ));
    var hours = sliderLeftDate.getHours();
    var am = true;
    if (hours > 12) {
       am = false;
       hours -= 12;
    } if (hours == 12) {
       am = false;
    } if (hours == 0) {
       hours = 12;
    }
    $( "#slider-left-value" ).val(weekday[sliderLeftDate.getDay()] + " " + sliderLeftDate.getMonth() + "/" + sliderLeftDate.getDate() + "/" + sliderLeftDate.getFullYear() + ": " + hours + (am ? "AM" : "PM"));


    sliderRightDate = convertToDate($( "#jmap-slider" ).slider( "values", 1 ));
    var hours = sliderRightDate.getHours();
    var am = true;
    if (hours > 12) {
       am = false;
       hours -= 12;
    } if (hours == 12) {
       am = false;
    } if (hours == 0) {
       hours = 12;
    }
    $( "#slider-right-value" ).val(weekday[sliderRightDate.getDay()] + " " + sliderRightDate.getMonth() + "/" + sliderRightDate.getDate() + "/" + sliderRightDate.getFullYear() + ": " + hours + (am ? "AM" : "PM"));

alert('hhk')
} 
