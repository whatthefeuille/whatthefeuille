<%inherit file="base.mako"/>

<script src="/media/js/jquery.cookie.js"></script>
<script src="/media/js/wtf.js"></script>

<h3>Upload a leaf snapshot</h3>

<p class="tip alert alert-info">Tip: try to put the leaf on a contrasted, unified background</p>

<form action="/upload" method="POST" id="uploadForm"
      enctype="multipart/form-data">

    <div class="fileupload">
        <img src="/media/camera_icon.png" id="uploadButton" title="Click here to upload a snapshot...">
        <input type="file" id="snap" accept="image/*;capture=camera" name="picture">
    </div>

    <input type="hidden" id="latitude" name="latitude">
    <input type="hidden" id="longitude" name="longitude">
    <input type="hidden" id="accuracy" name="accuracy">

    <div id="placeholder" class="map" style="width: 100%; height: 100%; position: relative;">
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
