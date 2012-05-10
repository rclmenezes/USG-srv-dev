/***************************************/
/* jqueryui setup */
/***************************************/

jDisplay = {}
function utilInit() {
	$("input:submit").button();
	$("#info-top-types").buttonset();
	
	//for the timeline
	jTimeline('info-jtl', getJTLParams());
	setupJTLInput();
	setupJTLDisplay();
	
}




/***************************************/
/* Timeline input */ 
/***************************************/

function setupJTLInput() {
	//nader's datepicker slider stuff
	//
	//end
	
	$('.jtl-params').change(function() {
		jTimeline('info-jtl', getJTLParams());
		handleFilterChange();
	});
}


/* Return dictionary of params in the input box for javascript */
function getJTLParams() {
	//var startDate = $('#jtl-startDate').datepicker("getDate");
	var inDate = $('#jtl-startDate').val().split('/');
	var startDate = new Date();
	clearDateTime(startDate);
	startDate.setFullYear(inDate[2]);
	startDate.setMonth(inDate[0]);
	startDate.setDate(inDate[1]);
	var nDays = $('#jtl-nDays').val();
	var startTime = $('#jtl-startTime').val().split(':');
	var endTime = $('#jtl-endTime').val().split(':');
	return {startDate:startDate, nDays:nDays, startTime:startTime, endTime:endTime};
}
/* Return dictionary of params in the input box for a GET request */
function getJTLParamsAJAX() {
	var p = getJTLParams();
	x= {
		m0: p.startDate.getMonth()+1,
		d0: p.startDate.getDate(),
		y0: p.startDate.getFullYear(),
		nDays: p.nDays,
		h0: p.startTime[0]%24,
		i0: p.startTime[1],
		h1: p.endTime[0]%24,
		i1: p.endTime[1],
	}
	return x;
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
		$(this).find('.jexpand-longdesc').show(100);
	});
	$('.jexpand-main').mouseout(function() {
		$(this).find('.jexpand-longdesc').hide(100);
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

