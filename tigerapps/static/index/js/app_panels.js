$(document).ready(

function() {

    var currentHash = location.hash.split("#");

    if (currentHash.length > 1) {

        var currentHashString = currentHash[1].toString();

        $("#navigation li a").removeClass("selected");

        $("#navigation li a[href*=" + currentHashString + "]").addClass("selected");

        var contentCollection = document.getElementsByTagName("li");

        for (i = 0; i < contentCollection.length; i++) {
            if (contentCollection[i].id) {
                if (contentCollection[i].id === currentHashString || currentHashString === "") {
                    $(contentCollection[i]).fadeIn(650);
                } else {
                    $(contentCollection[i]).fadeOut(650).css("display", "none");
                    if (location.hash !== "#") {
                        location.hash = "#" + currentHash[1];
                    } // if
                } // else
            } // if
        } // for
    } else {
        var contentCollection = document.getElementsByTagName("li");

        for (i = 0; i < contentCollection.length; i++) {
            if (contentCollection[i].id) {
                if (contentCollection[i].id !== "one") {
                    $(contentCollection[i]).fadeOut(650).css("display", "none");
                }
            } // if
        } // for
    } // else
    $("#navigation li a").click(function() {

        var myClicked = this.href.split("#");

        $("#navigation li a").removeClass("selected");

        this.className = "selected";

        var contentCollection = document.getElementsByTagName("li");

        for (i = 0; i < contentCollection.length; i++) {
            if (contentCollection[i].id) {
                if (contentCollection[i].id === myClicked[1]) {
                    $(contentCollection[i]).fadeIn(650);
                } else {
                    $(contentCollection[i]).fadeOut(650).css("display", "none");
                    if (location.hash !== "#") {
                        location.hash = "#" + myClicked[1];
                    }

                } // else
            } // if
        } // for
        return false;
    } // click func
    ); // click event
} // anon func 1
); // ready.
