
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
