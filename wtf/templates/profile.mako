<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:

<img src="${user_profile_picture}">

<p>Hello ${user.email}!</p>

<ul class="timeline">
    % for snap in snaps:
    <li>
        <a href="/snapshot/${basename(snap.filename)}">
            <img src="/thumbs/thumb/${basename(snap.filename)}">
        </a>
    </li>
    % endfor
</ul>
%endif
