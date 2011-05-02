#!/bin/sh

echo "Content-Type: text/html; iso-8859-1"
echo
cat <<PROLOGUE
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head><title>Kingman Hall: Internet Link</title>
<link rel="stylesheet" href="style.css" />
</head><body>
PROLOGUE

cat /web/internal/title.html
cat <<PAGE
<h1>Network Activity Log</h1>

PAGE

echo '<pre>'
tail -40 /web/internal/speed.txt
echo '</pre>'

cat <<EPILOGUE
<p class="footer">
<a href="http://validator.w3.org/check?uri=http://kingmanhall.org/internal/speed.cgi">
<img style="border: 0; width: 88px; height: 31px;"
     src="http://www.w3.org/Icons/valid-xhtml10"
     alt="Valid XHTML 1.0!" /></a>
<a href="http://jigsaw.w3.org/css-validator/validator?uri=http://kingmanhall.org/internal/speed.cgi">
<img style="border: 0; width: 88px; height: 31px;"
     src="http://jigsaw.w3.org/css-validator/images/vcss" 
     alt="Valid CSS!" /></a></p>
</body></html>
EPILOGUE
