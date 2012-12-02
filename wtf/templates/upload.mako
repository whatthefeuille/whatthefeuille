<%inherit file="base.mako"/>

<script src="/media/js/jquery.cookie.js"></script>
<script src="/media/js/wtf.js"></script>


<h3>Upload a snapshot of a leaf</h3>
<p>Try to put the leaf on a contrasted, unified background</p>
<form action="/upload" method="POST"
      enctype="multipart/form-data">

  <input type="file" accept="image/*;capture=camera" name="picture" />

  <input type="hidden" id="latitude" name="latitude"/>
  <input type="hidden" id="longitude" name="longitude"/>
  <input type="hidden" id="accuracy" name="accuracy"/>
   <div id="placeholder" style="margin: 20px 0px 10px; padding-left: 20px; width: 100%; height: 100%; position: relative;">
   </div>

  <div>
  <input type="submit"/>
  </div>
</form>
<script>
loadLocation();
</script>


