<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:

<img src="${user_profile_picture}">

<p>Hello ${user.email}!</p>

<ul>
    % for snap in snaps:
    <li>
        <img src="/thumb/small/${basename(snap.filename)}">
    </li>
    % endfor
</ul>
%endif
