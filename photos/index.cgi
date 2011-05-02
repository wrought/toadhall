#!/usr/bin/python -S

import sys, random
sys.path.append('/web/internal')
from utils import *

prologue('Kingman Hall Photo Album', '/style.css')

os.chdir('/web/photos')
folders = []
for filename in os.listdir('.'):
    if os.path.isdir(filename):
        stripped = filename.strip()
        if stripped[4:5] + stripped[7:8] + stripped[10:11] == '-- ':
            folders.append((stripped[:10], stripped[11:], filename))
folders.sort(lambda (ad, an, af), (bd, bn, bf): -2*cmp(ad, bd) + cmp(an, bn))

if folders:
    write(h1('Kingman Photo Album'))
    write(p, 'Want to add photos? ',
          link('README.txt', 'See the instructions.'), p)

    tmaker = TableMaker(3, 4, c='photos')
    year = 0
    for datetime, name, dir in folders:
        # Add the year heading.
        y, l, d = map(int, datetime.split('-'))
        if not (1 <= l <= 12):
            l = 0
        if y != year:
            tmaker.flush()
            write(h2(y))
            year = y

        # Get the list of photos in each folder.
        try:
            files = os.listdir(dir)
        except:
            files = [] # don't break if the directory has bad permissions
        files = filter(lambda n: not n.startswith('.'), files)
        files = filter(lambda n: n.lower().endswith('.jpg'), files)
        if not files:
            continue # don't show empty directories

        # Pick a random photo to show for each folder.
        filename = random.choice(files)
        path = join(dir, 'rotated', filename)
        if not isfile(path):
            path = join(dir, filename)
        preview = join(dirname(path), 'preview', filename)
        if not isfile(preview) or not getsize(preview):
            preview = 'preview.jpg'
        preview = cgi_encode(preview)

        # Prepare information for the caption.
        url = form_url('folder.cgi', folder=dir)
        date = '%s %s, %d' % (monthnames[l][:3], d, y)
        if not l or not d:
            date = str(y)
        count = '%d picture%s' % (len(files), plural(files))

        # Add three cells: the title, the photo, and the caption.
        tmaker.add(td(h3(link(url, name)), c='folder'),
                   td(link(url, img(preview, alt='preview')), c='photo'),
                   td(div(date, c='date'), div(count, c='count'), c='caption'))
    tmaker.flush()
else:
    write('No folders.')

epilogue()
