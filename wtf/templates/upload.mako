<%inherit file="base.mako"/>

<script src="/media/js/jquery.cookie.js"></script>
<script src="/media/js/wtf.js"></script>


<h3>Upload a snapshot of a leaf</h3>
<p>Try to put the leaf on a contrasted, unified background</p>
<form action="/upload" method="POST" id="uploadForm"
      enctype="multipart/form-data">

 <div class="fileupload">
  <img src="/media/camera_icon.png" id="uploadButton"/>
  <input type="file" id="snap" accept="image/*;capture=camera" name="picture" />
 </div>
  <input type="hidden" id="latitude" name="latitude"/>
  <input type="hidden" id="longitude" name="longitude"/>
  <input type="hidden" id="accuracy" name="accuracy"/>
   <div id="placeholder" style="width: 100%; height: 100%; position: relative;">
   </div>

  <div>
  </div>
</form>
<script>
  loadLocation();
 $("#snap").change(function() {
    if ($(this).val() != null) {
      $('#uploadForm').submit();
    }   
 });

  
  $('#uploadButton').click(function(e) {
    $('#snap').click();
  });
</script>


