#!/usr/bin/python

from utils import *
from fastcgi import form
import time

action = (form.action.lower().split() or [''])[-1]

if action == 'note':
    if not form.name.strip():
        abort('Maintenance: no name entered',
              "Please go back and enter something in the box for your name.")
    if not form.note.strip():
        abort('Maintenance: no text entered',
              'Please go back and enter some text for the note.')
    if form.id.strip():
        id = '>' + form.id
    else:
        id = '%.03f' % time.time()
    date = '%04d-%02d-%02d %02d:%02d' % time.localtime()[:5]
    name = ' '.join(form.name.split())
    note = form.note.replace('\r\n', '\n').replace('\n', '\x01')
    note = ' '.join(note.split()).replace('\x01', '\t')
    append_records(join(WEB_ROOT, 'maintenance.txt'), [(id, date, name, note)])
    redirect('maintenance.cgi')

if form.year:
    records = read_records('maintenance-%s.txt' % form.year, 4)
else:
    records = read_records('maintenance.txt', 4)

# Read the maintenance messages, attaching reply messages to their requests.

requests = []
replies = {}
for id, date, name, note in records:
    date, time = parse_date(date.split()[0]), date.split()[1]
    if id[:1] == '>':
        replies[id[1:]] = replies.get(id[1:], [])
        replies[id[1:]].append((date, time, name, note))
    else:
        requests.append((id, date, time, name, note))
        replies[id] = []
requests.reverse()

# Construct the table rows for the maintenance message board.

selector = ''
rows = []
parity = 'even'
for id, date, time, name, text in requests:
    if not form.year:
        rbutton = input(id=id, name='id', type='radio', value=id)
        rlabel = label('add a reply here', for_=id)
        selector = td(div(rbutton, rlabel, c='selector'), colspan=2)
    parity = (parity == 'even') and 'odd' or 'even'
    subrows = [format_note_cells(reply) for reply in replies[id]] + [selector]
    rows.append(trt(format_note_cells((date, time, name, text), len(subrows)),
                    subrows[0], c=parity))
    rows += [trt(subrow, c=parity) for subrow in subrows[1:]]
if form.year:
    rows.append('<script>disabled = 1</script>')

# Display the page.

prologue('Kingman Hall: Maintenance Board', 'style.css')
write_template('maintenance.html', notes=table(rows, c='notes'))
epilogue()
