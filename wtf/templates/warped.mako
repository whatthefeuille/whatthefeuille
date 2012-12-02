<%inherit file="base.mako"/>

<h3>Step 2/3 - Transformed image</h3>
<p>Click the image to edit the transformation</p>

<form action="." method="post">
    <div>
        <a href="/snapshot/${original}">
            <img src="/picture/${snapshot}"/>
        </a>
    </div>
    <div>
        <input type="submit" name="valid" value="Valid Alignment"/>
        <input type="submit" name="sucks" value="I want to redo it"/>
    </div>
</form>

