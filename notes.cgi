#!/usr/bin/python

from utils import *
from fastcgi import form, request

if form.year:
    notes = get_notes('notes-%s.txt' % form.year)
else:
    notes = get_notes()
notes.reverse()

import utils
utils.wiki = Wiki('kwiki-data')
utils.wikiurl = request.rsplit('/', 1)[0] + '/kwiki'

prologue('Kingman Hall: All Notes', 'style.css')
write_template('all-notes.html', notes=table(map(format_note, notes)))
epilogue()
