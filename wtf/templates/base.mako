<!doctype html>
<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

  <link href='/media/wtf.css' rel='stylesheet' type='text/css'/>
  <link rel="shortcut icon" href="/media/small-logo.png">
  <title>What The Feuille</title>
</head>
  <body>
    <div id="header">
        <img src="/media/logo.png"/>
        <a href="/" id="title">What The Feuille</a>
        <span id="subtitle">Recognizing your leaves since 2012</span>
      <div class="login">
        %if user:
        Hi <a href="/profile">${user}</a>. <a href="/logout">Logout.</a>
        %endif
        %if not user:
        <a href="/sign"><img src="/media/sign_in_blue.png"/></a>
      %endif
      </div>

       %if messages:
         %for message in messages:
         <div class="message">
            ${message}
         </div>
       %endfor
     %endif
    </div>
    <div style="clear:both"></div>
     <div id="body">
       ${self.body()}
   </div>

  </body>
</html>
