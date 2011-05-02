#!/usr/bin/python -S

import sys, os, exif, time
sys.path.append('/web/internal')
from utils import *
from rotation import *
from fastcgi import form

try:
    os.chdir('/web/photos/' + form.folder)
except:
    abort('No such folder',
          'There is no folder named "', span(esc(form.folder), c='error'), '".')

if not isfile(form.name):
    abort('No such file',
          'There is no image named "', span(esc(form.name), c='error'),
          '" in the folder "', span(esc(form.folder), c='error'), '".')

key = join(form.folder, form.name)
start_work(key) # note the time that work started

original = form.name
preview = join('preview', form.name)
rotated_temp = '/tmp/rtemp-%d.jpg' % os.getpid()
rotated = join('rotated', form.name)
rotated_preview = join('rotated', 'preview', form.name)
preview_temp = '/tmp/ptemp-%d.jpg' % os.getpid()
mkdir(dirname(rotated))
mkdir(dirname(rotated_preview))

if isfile(rotated) and get_orient(rotated) == int(form.orient or 1):
    # already rotated correctly
    finish_work(key)
else:
    xform = transform(get_orient(original), int(form.orient or 1))
    if rotate_image(original, xform, rotated_temp):
        if isfile(preview):
            rotate_image(preview, xform, preview_temp, skip_orient=1) # fast
        else:
            make_preview(rotated_temp, 200, preview_temp) # slow
        if finish_work(key): # prevent earlier work from overwriting later work
#            os.rename(rotated_temp, rotated)  #doesn't work across diff. devices
#            os.rename(preview_temp, rotated_preview)
            os.system('cp "%s" "%s"' % (rotated_temp, rotated))
            os.system('cp "%s" "%s"' % (preview_temp, preview))
            remove(rotated_temp)
            remove(preview_temp)
        else:
            remove(rotated_temp)
            remove(preview_temp)
            wait_work(key)
    else:
        rotated_preview = preview

write('Content-Type: image/jpeg\n\n')
write(open(rotated_preview).read())
