var TABS = $('#basicinfo, #pending');
var CLIQUES = $('#click1, #click3');
function updateTabs(tabid, clickid) {
    TABS.hide();
    tabid = '#' + tabid;
    $(tabid).show();

    var toclick = document.getElementById(clickid);
    CLIQUES.removeClass('selectedtab');
    clickid = '#' + clickid;
    $(clickid).addClass('selectedtab');
}

if($('.selectedtab').length == 0) {
    updateTabs('basicinfo', 'click1');
}
