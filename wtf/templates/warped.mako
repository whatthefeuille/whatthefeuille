<%inherit file="base.mako"/>

%if not snap.plant:
  <h3>Step 2/3 - Transformed image</h3>
  <p>Find the best matching plant among the suggestions.</p>
%else:
  <h3>Leaf from ${snap.plant}</h3>
%endif
 
<p>Click the image to edit the transformation.</p>

<form action="." method="post">
  <div>
    <a href="/snapshot/${original}">
      <img src="/picture/${snapshot}"/>
    </a>
  </div>
</form>

%if not snap.plant:
<h3>Suggestions</h3>
<p>Here's a list of plant suggestions, pick the one that fits</p>

%for plant, data in suggestions.items():
<div class="suggestion">
  <h3>${plant}</h3>
  <div class="suggestedPlant">
  %if data[0].filename:
    <img src="/thumbs/medium/${data[0].filename}"/>
  %else:
     <img src="/media/tree_icon.png"/>
  %endif
 </div>
 <div class="leafs">  
  %for leaf in data[1]:
    <img src="/thumbs/small/${leaf.filename}"/>
  %endfor
  </div>
</div>
%endfor

%endif
