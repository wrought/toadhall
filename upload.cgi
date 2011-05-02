#!/usr/bin/python -S

from utils import *
from fastcgi import os, client, request, form, files

prologue('Kingman Hall Home Page', 'style.css')

if form.file:
    print 'File received: ', len(files.file), ' bytes.'
    print p, 'Name:', esc(form.file)
    print p, 'Start: ', esc(repr(files.file[:20]))
    print p, 'End: ', esc(repr(files.file[-20:]))

else:
    print '''
<form method="post" enctype="multipart/form-data">
<input name="file" type="file">
<input type="submit">
</form>
    '''
