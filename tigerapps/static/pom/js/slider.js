//This contains all the code to make the slider work.

function convertToDate(sliderVal) {
    return sliderVal;
}

function sliderInit() {
    $( "#jmap-slider" ).slider({
        range: true,
        min: 0,
        max: 500,
        values: [0, 500],
        slide: function( event, ui ) {
            $( "#slider-left-value" ).val( ui.values[ 0 ] );
            sliderLeftDate = convertToDate(ui.values[0]);
            $( "#slider-right-value" ).val( ui.values[ 1 ] );
            sliderRightDate = convertToDate(ui.values[1]);
        }
    });
    $( "#slider-left-value" ).val($( "#jmap-slider" ).slider( "values", 0 ));
    sliderLeftDate = convertToDate($( "#jmap-slider" ).slider( "values", 0 ));
    $( "#slider-right-value" ).val($( "#jmap-slider" ).slider( "values", 1 ) );	
    sliderRightDate = convertToDate($( "#jmap-slider" ).slider( "values", 1 ));

alert('hhk')
} 
