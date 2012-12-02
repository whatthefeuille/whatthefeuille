<%inherit file="base.mako"/>

<h3>Upload a snapshot of a leaf</h3>
<p>Try to put the leaf on a contrasted, unified background</p>
<form action="/upload" method="POST"
      enctype="multipart/form-data">

  <input type="file" accept="image/*;capture=camera" name="picture" />
  <div>
  <input type="submit"/>
  </div>
</form>
