<%inherit file="base.mako"/>

<form action="/upload" method="POST"
      enctype="multipart/form-data">

  <input type="file" accept="image/*;capture=camera" name="picture" />
  <input type="submit"/>
</form>
