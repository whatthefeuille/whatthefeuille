
var current_button = 1;

$("#pointer_div").click(function(e) {

    var div = $("#pointer_div");

    var pos_x = e.pageX - div.position().left;
    var pos_y = e.pageY - div.position().top;

    console.log(pos_x);
    console.log(pos_y);

    if (current_button == 1) {
        $("#top_x").val(pos_x);
        $("#top_y").val(pos_y);
        current_button = 2;
        var cross = $("#topcross");
        cross.css('left', pos_x - 25);
        cross.css('top', pos_y);
        cross.show();
        $("#step").text("Select the bottom of the leaf.");
        $(".snapshot").attr("title", "Select the bottom of the leaf.");
    }
    else {
        $("#bottom_x").val(pos_x);
        $("#bottom_y").val(pos_y);
        current_button = 1;
        var cross = $("#bottomcross");
        cross.css('left', pos_x - 25);
        cross.css('top', pos_y - 50);
        cross.show();
        $("#step").text("Select the top of the leaf.");
        $(".snapshot").attr("title", "Select the top of the leaf.");
        $('input[type="submit"]').removeAttr('disabled');
    }
});


var latitude;
var longitude;
var accuracy;

function loadLocation() {
  if (navigator.geolocation) {
    
    if ($.cookie("posLat")) {
	latitude = $.cookie("posLat");
	longitude = $.cookie("posLon");
	accuracy = $.cookie("posAccuracy");
	updateDisplay();
	
    } else {
	navigator.geolocation.getCurrentPosition(
			    success_handler, 
			    error_handler, 
			    {timeout:10000});
    }
}
}

function success_handler(position) {
  latitude = position.coords.latitude;
  longitude = position.coords.longitude;
  accuracy = position.coords.accuracy;

  if (!latitude || !longitude) {
    return;
  }

  updateDisplay();
  $.cookie("posLat", latitude);
  $.cookie("posLon", longitude);
  $.cookie("posAccuracy", accuracy);
}

function updateDisplay() {

  var gmapdata = '<img src="http://maps.google.com/maps/api/staticmap?center=' + latitude + ',' + longitude + '&zoom=16&size=425x350&sensor=false" />';
   document.getElementById("placeholder").innerHTML = gmapdata;
   $("#latitude").val(latitude);
   $("#longitude").val(longitude);
   $("#accuracy").val(accuracy);
}


function error_handler(error) {

  var locationError = '';

 switch(error.code){
  case 0:
    locationError = "There was an error while retrieving your location: " + error.message;
    break;
  case 1:
    locationError = "The user prevented this page from retrieving a location.";
    break;
  case 2:
    locationError = "The browser was unable to determine your location: " + error.message;
    break;
  case 3:
    locationError = "The browser timed out before retrieving the location.";
    break;
  }

}

function clear_cookies() {
  $.cookie('posLat', null);
}


