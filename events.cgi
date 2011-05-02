#!/usr/bin/python

from utils import *
from fastcgi import form, request

if form.year:
    events = get_events('events-%s.txt' % form.year)
else:
    events = get_events()
events.sort()
events.reverse()

import utils
utils.wiki = Wiki('kwiki-data')
utils.wikiurl = request.rsplit('/', 1)[0] + '/kwiki'

prologue('Kingman Hall: All Events', 'style.css')
write_template('all-events.html', events=table(map(format_event, events)))
epilogue()
