<%inherit file="base.mako"/>

<h3>${name}</h3>
<img id="plant" src="${image}"/>

<ul class="timeline">
    % for snap in snaps:
     % if snap.warped:
      <li class="warped"> 
        <a class="image" href="/warped/${snap.warped_filename}"
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

<form action="/upload_plant_snaps" method="POST" id="uploadForm"
      enctype="multipart/form-data">

  <input type="file" multiple="multiple" name="snap"/>
  <input type="hidden" name="name" value="${name}"/>
  <input type="submit"/>
<form>

