#!/usr/bin/python -S

import sys, exif, re
sys.path.append('/web/internal')
from time import localtime
from utils import *
from fastcgi import form

fluff = re.compile(
    r'\s+(Inc|Digital Camera|Camera|Co|Ltd)([:,. ]|\s*$)\s*', re.I)

def get_image_info(path):
    try:
        info = exif.parse(path)
    except:
        info = {}
    y = l = d = 0
    datetime = info.get('DateTimeOriginal',
                        info.get('DateTimeDigitized',
                                 info.get('DateTime', '')))
    if datetime:
        date, time = datetime.split(' ')
        y, l, d = map(int, date.split(':'))
        h, m, s = map(int, time.split(':'))
    if y == 0 or l == 0 or d == 0:
        y, l, d, h, m, s = localtime(getmtime(path))[:6]
    make = info.get('Make', '')
    model = info.get('Model', '')
    if make.strip() and make.split()[0].lower() not in model.lower():
        model = make.split()[0] + ' ' + model
    model = re.sub(fluff, ' ', model)
    words = info.get('Flash', '').lower().split()
    flash = words and 'no flash' or ''
    if 'fired' in words:
        if 'fill' in words:
            flash = 'fill flash'
        elif 'auto' in words:
            flash = 'auto flash'
        else:
            flash = 'flash'
    orient = int(info.get('Orientation', 1) or 1)
    return (y, l, d, h, m, s), model, flash, orient

def get_jpeg_size(path):
    try:
        file = open(path)
        if file.read(2) != '\xff\xd8':
            return 0, 0
        while 1:
            type = file.read(2)
            length = ord(file.read(1))*256 + ord(file.read(1))
            if type == '\xff\xc0':
                precision = file.read(1)
                height = ord(file.read(1))*256 + ord(file.read(1))
                width = ord(file.read(1))*256 + ord(file.read(1))
                return width, height
            else:
                file.seek(length - 2, 1)
    except (IOError, TypeError):
        return 0, 0

date = form.folder.strip()[:10]
name = form.folder.strip()[11:]

prologue('Kingman Hall Photo Album: %s %s' % (date, name), '/style.css')
try:
    year = int(date[:4])
    l = int(date[5:7])
    d = int(date[8:10])
    date = '%s %d, %d' % (monthnames[l][:3], d, year)
    if not l or not d:
        date = str(year)
except:
    abort('Invalid folder name: %s' % esc(form.folder))
write(h1('%s (%s)' % (esc(name), date)))
write(p, 'Back to ', link('index.cgi', 'index of folders'), '.', p)

try:
    os.chdir('/web/photos/' + form.folder)
    os.chdir('/web/photos')
except:
    abort('No such folder',
          'There is no folder named "', span(esc(form.folder), c='error'), '".')

write('''
<div class="hidden" id="hidden">
<div class="turners" id="turners" onmouseover="enter()" onmouseout="exit()">
<div><img src="turn-ccw.png" onclick="ccw()"
><img src="turn-cw.png" onclick="cw()"></div>
</div>
</div>
<script>
function $(id) { return document.getElementById(id); }

var turn_cw = [0, 8, 7, 6, 5, 2, 1, 4, 3];
var turn_ccw = [0, 6, 5, 8, 7, 4, 3, 2, 1];

var folder = %r;
var hidden = $('hidden'), turners = $('turners');
var index, orientations = {}, filenames = {}, busy = {}, opacity = {};

function enter(i, orient, filename) {
    if (i) {
        index = i;
        if (!orientations[index]) orientations[index] = orient;
        filenames[index] = filename;
    }
    $('c' + index).appendChild(turners);
}
function exit() { hidden.appendChild(turners); }
function ccw() { rotate(turn_ccw[orientations[index]], 'ccw.gif'); }
function cw() { rotate(turn_cw[orientations[index]], 'cw.gif'); }

function fade(index) {
    if (busy[index]) {
        opacity[index] = (opacity[index]*3 + 0.3)/4;
        $('i' + index).style.opacity = opacity[index];
        if (opacity[index] > 0.31) setTimeout('fade(' + index + ')', 50);
    }
}
function rotate(orient, background) {
    orientations[index] = orient;
    $('p' + index).style.backgroundImage = 'url(' + background + ')';
    busy[index] = 1; opacity[index] = 1.0; fade(index);
    $('i' + index).setAttribute('onload', 'finish(' + index + ')');
    $('i' + index).src = 'rotate.cgi?orient=' + orient +
                         '&folder=' + escape(folder) +
                         '&name=' + escape(filenames[index]) +
                         '&time=' + new Date().getTime();
}
function finish(index) {
    busy[index] = 0;
    $('p' + index).style.backgroundImage = 'none';
    $('i' + index).style.opacity = '';
    $('a' + index).setAttribute(
        'href', escape(folder + '/rotated/' + filenames[index]));
}
</script>
''' % form.folder)

pictures = []
for filename in os.listdir(form.folder):
    if filename.startswith('.') or not filename.lower().endswith('.jpg'):
	continue
    path = join(form.folder, 'rotated', filename)
    if not isfile(path):
        path = join(form.folder, filename)
    if isfile(path):
        datetime, model, flash, orient = get_image_info(path)
        size = get_jpeg_size(path)
        pictures.append((datetime, filename, path, size, model, flash, orient))
pictures.sort()

tmaker = TableMaker(2, 4, c='photos')
i = 0
for datetime, filename, path, size, model, flash, orient in pictures:
    y, l, d, h, m, s = datetime
    date = '%s %s, %02d:%02d' % (monthnames[l][:3], d, h, m)
    if y != year:
        date = '%s %s, %d, %02d:%02d' % (monthnames[l][:3], d, y, h, m)
    size = '%d<small>&times;</small>%d' % size
    preview = join(dirname(path), 'preview', filename)
    if not isfile(preview) or not getsize(preview):
        preview = 'preview.jpg'
    path, preview = cgi_encode(path), cgi_encode(preview)
    i += 1
    attrs = {'onmouseover': "enter(%d, %d, %r)" % (i, orient, filename),
             'onmouseout': "exit()"}
    tmaker.add(td(link(path, img(preview, id='i%d' % i), id='a%d' % i),
                  id='p%d' % i, c='photo', **attrs),
               td(div(date, c='date'), div(size, c='time'),
                  div(model, c='model'), div(flash, c='flash'),
                  id='c%d' % i, c='caption', **attrs))
# A Firefox bug causes photos in the last row to move one cell to the right
# when rotating, if the last row is not full (less than 4 photos).  Fill
# the last row with empty cells to avoid this bug.
tmaker.flush(td(c='photo'), td(c='caption'))
