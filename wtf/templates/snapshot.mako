<%inherit file="base.mako"/>


<h3 id="step">Select the top of the leaf</h1>
<form name="pointform" method="post">
  <div id="pointer_div" style = "background-image:url('/picture/${snapshot}');width:500px;height:333px;position:relative">
    <img src="/media/top.gif" id="topcross" style="position:absolute"></img>
    <img src="/media/bottom.gif" id="bottomcross" 
style="position:absolute"></img>

  </div>
  
 <div> 
   <input type="text" id="top_x" name="top_x" size="4" /> 
  - y = <input type="text" id="top_y" name="top_y" size="4" />
 </div>
 <div>
   <input type="text" id="bottom_x" name="bottom_x" size="4" /> 
  - y = <input type="text" id="bottom_y" name="bottom_y" size="4" />

 </div>


</form>

<script src="/media/js/wtf.js"></script>

<script>
$(document).ready(function() {
   $('#topcross').hide();
   $('#bottomcross').hide();

 });
</script>

