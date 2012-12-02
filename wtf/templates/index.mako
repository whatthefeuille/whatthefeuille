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
    <li>
        % if snap.warped:
        <a class="image" href="/warped/${basename(snap.filename)}"
           style="background-image: url('/thumbs/large/${basename(snap.warped_filename)}')">
        </a>
        % else:
        <a class="image" href="/snapshot/${basename(snap.filename)}" 
           style="background-image: url('/thumbs/large/${basename(snap.filename)}')">
        </a>
         % endif
        <div class="bar">
            <div class="date">Posted on ${format_date(snap.timestamp)}</div>
        </div>
    </li>
    % endfor
</ul>

