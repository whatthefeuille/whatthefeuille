<%inherit file="base.mako"/>

<ul class="timeline">

   <li>
     <a class="image add" href="/upload_plant"
          style="background-image: url('/media/add.png')">
     </a>
     <div class="bar">
       <div class="date">Add a new plant...</div>
     </div>
   </li>
    % for plant in plants:
    <li>
        %if plant.filename:
        <a class="image" href="/plant/${plant.name}"
           style="background-image: url('/thumbs/large/${plant.filename}')">
        </a>
        %endif
        %if not plant.filename:
        <a class="image" href="/plant/${plant.name}"
          style="background-image: url('/media/tree_icon.png')">
             <span>${plant.name}<span>
             <p>put a generic image here. </p>
        </a>
        %endif
        <div class="bar">
            <div class="date">Posted on ${format_date(plant.timestamp)}</div>
        </div>
    </li>
    % endfor
</ul>

