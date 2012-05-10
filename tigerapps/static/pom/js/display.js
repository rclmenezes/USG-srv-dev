/***************************************/
/* jqueryui setup */
/***************************************/

jDisplay = {}
function utilInit() {
	$("input:submit").button();
	$("#info-top-types").buttonset();

	//nader's datepicker slider stuff
	//
	//end
	
	//for the timeline
	setupJTLDisplay();
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
/* Utility functions */
/***************************************/

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

function clearDateTime(d) {
	d.setHours(0);d.setMinutes(0);d.setSeconds(0);d.setMilliseconds(0);
}

function handleAjaxError(jqXHR, textStatus, errorThrown) {
    if (confirm(errorThrown + ': Show error?')) {
        win = window.open();
        win.document.write(jqXHR.responseText);
    }
}

