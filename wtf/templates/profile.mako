<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:
<ul class="timeline">
    % for snap in snaps:
    <li>
        <a class="image" href="/snapshot/${snap.filename}"
          style="background-image: url('/thumbs/large/${snap.filename}')">
        </a>
        <div class="bar">
          <div class="date">Posted on ${format_date(snap.timestamp)}</div>
        </div>
    </li>
    % endfor
</ul>
%endif
