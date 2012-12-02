<%inherit file="base.mako"/>

<ul class="timeline">
   <li>
     <a class="image" href="/upload"
          style="background-image: url('/media/add.png')">
     </a>
    <div class="bar">
            <div class="date">Add a new snapshot...</div>
        </div>

   </li>
    % for snap in snaps:
        % if snap.warped:
      <li class="warped">
        <a class="image add" href="/warped/${snap.warped_filename}"
           style="background-image: url('/thumbs/large/${snap.warped_filename}')">
        </a>
        % else:
       <li>
        <a class="image" href="/snapshot/${snap.filename}"
           style="background-image: url('/thumbs/large/${snap.filename}')">
        </a>
         % endif
        <div class="bar">
          <div class="date">
            %if snap.plant:
            ${snap.plant} - 
            %endif
           <em>Posted on ${format_date(snap.timestamp)}</em>
          </div>
        </div>
    </li>
    % endfor
</ul>

