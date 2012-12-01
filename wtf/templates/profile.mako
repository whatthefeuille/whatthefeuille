<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:

<img src="${gravatar(user.email)}">

<p>Hello ${user.email}!</p>

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
%endif
