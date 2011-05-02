#!/usr/bin/python

from utils import *
from fastcgi import form, client
from time import time, strftime, localtime

prologue('Kingman Hall: Upload Registration', 'style.css')
now = time()

print '<h1>Upload Registration</h1>'

name = form.name.strip()
if not name:
    print "<p>Sorry, you didn't enter your name."
elif not client.startswith('10.0.'):
    print "<p>Sorry, your IP address is %s, which isn't in Kingman." % client
else:
    expiry = now + 15 * 60
    lt = localtime(expiry)
    print '<p>Okay.  IP address %s is registered to hog the link until' % client
    print strftime('%H:%M:%S', lt), 'on', strftime('%d %B %Y', lt) + '.'
    file = open('/web/internal/permits.txt', 'a')
    file.write('%d %s - %s\n' % (expiry, client, name))
    file.close()
