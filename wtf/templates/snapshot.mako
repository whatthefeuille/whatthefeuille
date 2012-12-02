<%inherit file="base.mako"/>

<h3>Step 1/3 - Align your leaf!</h3>
<p id="step">Select the top of the leaf</p>

<form id="pointform" name="pointform" method="post" action="/snapshot/${snapshot}">
    <div class="snapshot" id="pointer_div" style="background-image: url('/picture/${snapshot}'); width: ${width}px; height:${height}px" title="Select the top of the leaf">
        <img src="/media/top.png" id="topcross">
        <img src="/media/bottom.png" id="bottomcross">
    </div>
    <div style="float: left">
    %if warped_image:
        <img src="/picture/${warped_image}">
    %endif
    </div>
    <div style="clear:both"/>
    <input type="hidden" id="top_x" name="top_x">
    <input type="hidden" id="top_y" name="top_y">
    <input type="hidden" id="bottom_x" name="bottom_x">
    <input type="hidden" id="bottom_y" name="bottom_y">
</form>

<script src="/media/js/wtf.js"></script>

<script>
$(document).ready(function() {
   $('input[type="submit"]').attr('disabled', 'disabled');
   $('#topcross').hide();
   $('#bottomcross').hide();
});
</script>
