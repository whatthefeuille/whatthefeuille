<%inherit file="base.mako"/>

<h3>Step 1/3 - Align your leaf!</h3>
<p id="step">Select the top of the leaf</p>

<form name="pointform" method="post" action="/snapshot/${snapshot}">
  <div id="pointer_div" style =
"background-image:url('/picture/${snapshot}');width:${width}px;height:${height}px;position:relative">
    <img src="/media/top.gif" id="topcross" style="position:absolute"></img>
    <img src="/media/bottom.gif" id="bottomcross"
style="position:absolute"></img>

  </div>

<input type="hidden" id="top_x" name="top_x" />
<input type="hidden" id="top_y" name="top_y"  />
<input type="hidden" id="bottom_x" name="bottom_x" />
<input type="hidden" id="bottom_y" name="bottom_y" />

<input type="submit" value="Looks good! " name='ok'/>
</form>

<script src="/media/js/wtf.js"></script>

<script>
$(document).ready(function() {
   $('#topcross').hide();
   $('#bottomcross').hide();

 });
</script>
