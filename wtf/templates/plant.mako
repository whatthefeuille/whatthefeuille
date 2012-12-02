<%inherit file="base.mako"/>

<h3>${name}</h3>
<img src="${image}"/>

<ul class="timeline">
    % for snap in snaps:
    <li>
        <a class="image" href="/snapshot/${basename(snap.filename)}" style="background-image: url('/thumbs/large/${basename(snap.filename)}')">
        </a>
        <div class="bar">
            <div class="date">Posted on ${format_date(snap.timestamp)}</div>
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

