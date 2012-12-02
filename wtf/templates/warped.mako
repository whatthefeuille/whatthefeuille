<%inherit file="base.mako"/>

<h3>Step 2/3 - Transformed image</h3>
<p>Find the best matching plant among the suggestions.</p>
<p>Click the image to edit the transformation.</p>

<form action="." method="post">
  <div>
    <a href="/snapshot/${original}">
      <img src="/picture/${snapshot}"/>
    </a>
  </div>
</form>

