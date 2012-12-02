<%inherit file="base.mako"/>



<h3>Create a new plant.</h3>

<form action="/upload_plant" method="POST" id="uploadForm"
      enctype="multipart/form-data">
 <div>
  <input type="file" accept="image/*;capture=camera" name="picture" />
 </div>
 <div>
   <input type="text" name="name"/>
 </div>
 <div>
   <input type="submit" name="ok"/>
 </div>

</form>
 
