<%inherit file="base.mako"/>

%if not snap.plant:
  <h3>Step 2/3 - Transformed image</h3>
  <p>Find the best matching plant among the suggestions.</p>
%else:
  <h3>Leaf from ${snap.plant}</h3>
%endif

<form action="." method="post">
  <div>
    <a href="/snapshot/${original}">
      <img src="/picture/${snapshot}"/>
    </a>
  </div>
</form>

<p class="tip alert alert-info">Tip: click on the image if you want to correct the leaf alignment.</p>


%if not snap.plant:
<hr>
<h3>Suggestions</h3>
<p>Here's a list of plant suggestions, pick the one that fits:</p>

%for i, (plant, data) in enumerate(suggestions.items(), start=1):
<div class="suggestion">
  <h4>${i}. ${plant}</h4>
  <div class="suggestedPlant">
  <form action="/pick" method="POST" id="pick Form"
      enctype="multipart/form-data">

  %if data[0].filename:
    <img src="/thumbs/medium/${data[0].filename}"/>
  %else:
     <img src="/media/tree_icon.png"/>
  %endif
   <input type="hidden" name="plant" value="${plant}"/>
   <input type="hidden" name="leaf" value="${uuid}"/>
   <input type="submit" value="Pick!" name="pick"/>
  </form>
 </div>
 <div class="leafs">
  %for leaf in data[1]:
    <img src="/thumbs/small/${leaf.filename}"/>
  %endfor
  </div>
</div>
%endfor
%endif

%if next_snap:
<hr>
<h3>There are ${unwarped_count} more snapshots of ${snap.plant} to warp</h3>

<p><a href="/snapshot/${next_snap.filename}">Warp next!</a></p>
%endif
