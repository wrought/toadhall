#!/usr/bin/python -S

from utils import *
from fastcgi import os, client, request, form
import random

past_events = 10 
future_events = 10
max_events = 20
max_notes = 30

prologue('Kingman Hall Home Page', 'style.css')

borkify = not random.randrange(30)
if borkify and not form.preview:
    # Replace the existing "write" routine with one that sends all text
    # through a Swedish Chef filter.
    chef = os.popen2("./chef")
    def write(*stuff):
        chef[0].write(flatten(stuff))
    import utils
    utils.write = write

# Status bar.

write_template('status.html',
               dns=read_file('/tmp/status.dns'),
               printer=read_file('/tmp/status.printer'),
               toner=get_toner_records(1).values()[0]['black_cartridge'] or '?',
               half_fish=read_file('/tmp/status.half-fish'),
               jukebox=read_file('/tmp/status.jukebox'),
               dsl=read_file('/tmp/status.dsl'))

# Links section.

voc_members = {}
for line in read_lines('voc-members.txt'):
    voc_members[line.strip()] = 1
if 'comment-only' in voc_members:
    del voc_members['comment-only']
voc_done = len(voc_members)
voc_needed = int((50 + 9) * 0.9 + 0.999)

quotients, counts = get_hotness('do', {'m': 26, 'f': 26})
hq = percentage(quotients[('any', 'any')])
fhq = percentage(quotients[('any', 'f')])
mhq = percentage(quotients[('any', 'm')])

write_template('links.html',
               voc_count=voc_done,
               voc_percent='%.1f' % (voc_done/59.0),
               hotness_quotient=hq)

# Announcement.

announcement = read_file('announcement.txt')
if announcement.strip():
    write(div(announcement, c='announcement'))

# Event listing and message board.

import utils
utils.wiki = Wiki('kwiki-data')
utils.wikiurl = request.rsplit('/', 1)[0] + '/kwiki'

events = get_events()
events.sort()
today = get_date()
first, last = 0, len(events)
for i in range(len(events)):
    date, title, details = events[i]
    if date < today:
        first = i
    if date > today:
        last = i
        break
nearby = events[max(first - past_events, 0):
                min(last + future_events, len(events))][-max_events:]

event_rows = map(format_event, reversed(nearby))
see_all = link('events.cgi', '(see all %d events)' % len(events))
event_rows.append(tr(td(see_all, colspan=2)))

upcoming_rows = map(format_event, [e for e in nearby if e[0] >= today])
recent_rows = map(format_event, reversed([e for e in nearby if e[0] < today]))
recent_rows.append(tr(td(see_all, colspan=2)))

today = [(date, t, d) for (date, t, d) in events if date == today]
today_rows = map(format_event, today)
today_section = [div(h2('Today'), c='heading'),
                 div(table(today_rows), c='today content')]
if not today_rows:
    today_section = []

notes = get_notes()
notes.reverse()

note_rows = map(format_note, notes[:max_notes])
see_all = link('notes.cgi', '(see all %d notes)' % len(notes))
note_rows.append(tr(td(see_all, colspan=2)))

def sel_option(text, value, current):
    sel = [None, 'selected'][str(value) == str(current)]
    return option(text, value=value, selected=sel)

# Show only the next six months as options.
month_options = [sel_option('month', '', form.month)]
y, l = time.localtime()[:2]
suffix = ''
for i in range(6):
    text = monthnames[l][:3] + suffix
    month_options.append(sel_option(text, '%04d-%02d' % (y, l), form.month))
    l += 1
    if l > 12:
        y, l = y + 1, 1
        suffix = ' %d' % y # indicate year rollover
day_options = [sel_option('day', '', form.day)
          ] + [sel_option(i, i, form.day) for i in range(1, 32)]

event_preview = ''
if form.preview and form.title:
    date = parse_date(form.month + '-' + form.day)
    event_preview = table(format_event((date, form.title, form.details)))

note_preview = ''
if form.preview and form.name:
    y, l, d, h, m, s = time.localtime()[:6]
    note_preview = table(format_note(
        (Date(y, l, d), '%02d:%02d' % (h, m), form.name, form.note)))

write_template('events-notes.html', today=today_section,
               upcoming=table(upcoming_rows), recent=table(recent_rows),
               events=table(event_rows), notes=table(note_rows),
               month_options=month_options, day_options=day_options,
               title=esc(form.title), details=esc(form.details),
               name=esc(form.name), note=esc(form.note),
               event_preview=event_preview, note_preview=note_preview)

try:
    epilogue()
except SystemExit:
    if borkify:
        chef[0].close()
        print chef[1].read()
