<%inherit file="base.mako"/>

%if not user:
  <a href="/sign">Sign in with Browser-ID</a>
%endif

%if user:
<p>Hello ${user.email}!</p>
%endif

