#!/usr/bin/env python

from utils import *
from fastcgi import form
import time, socket

if form.text:
    text = form.text.replace('"', "'").replace('\\', '')
    s = socket.socket()
    s.connect(('Jukebox', 1314))
    s.send('(SayText "%s")\n' % text)
    s.close()

prologue('Kingman Hall: The Voice of Half-Fish', 'style.css')
write_template('speak.html')
epilogue()
