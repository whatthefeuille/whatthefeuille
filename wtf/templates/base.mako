<!doctype html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link href='/media/wtf.css' rel='stylesheet' type='text/css'/>
    <link href='/media/bootstrap.css' rel='stylesheet' type='text/css'/>
    <meta name="viewport" content="width=device-width">

    <script src="/media/js/jquery.js"></script>
    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
    </style>

    <link href='/media/bootstrap-responsive.css' rel='stylesheet' type='text/css'/>
    <link rel="shortcut icon" href="/media/leaf-16x16.png">
    <title>What The Feuille</title>
  </head>
  <body>
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/">What The Feuille</a>
          <div class="nav-collapse collapse">
            <ul class="nav">
              <li><a href="/plant">Plants</a></li>
              <li><a href="/upload">Upload</a></li>
              %if user:
              <li>
              <a href="/profile">
                <img src="${gravatar(user.email)}" width="20" height="20"/>
                ${user.email}
              </a>
              </li>
              <li><a href="/logout">Logout</a></li>
              %endif
              <li><a href="/about">About</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">
      %if messages:
      %for message in messages:
      <div class="alert alert-info">
          <button type="button" class="close" data-dismiss="alert">×</button>
          <p>${message}</p>
      </div>
      %endfor
      %endif

      ${self.body()}

      <hr>
      <footer>
      <p>&copy; Ronan - Olivier - Tarek - 2012 -- Recognizing your leaves since
      2012</p>
      </footer>

    </div>
    <script src="/media/js/bootstrap-transition.js"></script>
    <script src="/media/js/bootstrap-alert.js"></script>
    <script src="/media/js/bootstrap-modal.js"></script>
    <script src="/media/js/bootstrap-dropdown.js"></script>
    <script src="/media/js/bootstrap-scrollspy.js"></script>
    <script src="/media/js/bootstrap-tab.js"></script>
    <script src="/media/js/bootstrap-tooltip.js"></script>
    <script src="/media/js/bootstrap-popover.js"></script>
    <script src="/media/js/bootstrap-button.js"></script>
    <script src="/media/js/bootstrap-collapse.js"></script>
    <script src="/media/js/bootstrap-carousel.js"></script>
    <script src="/media/js/bootstrap-typeahead.js"></script>
  </body>
</html>
