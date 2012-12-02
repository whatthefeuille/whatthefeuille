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
        <a class="image" href="/warped/${snap.warped_filename}"
           style="background-image: url('/thumbs/large/${snap.warped_filename}')">
        </a>
        % else:
        <a class="image" href="/snapshot/${snap.filename}"
           style="background-image: url('/thumbs/large/${snap.filename}')">
        </a>
         % endif
        <div class="bar">
            <div class="date">Posted on ${format_date(snap.timestamp)}</div>
        </div>
    </li>
    % endfor
</ul>

