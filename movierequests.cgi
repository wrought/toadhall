#!/usr/bin/python

from utils import *
from fastcgi import form

if form.year:
    records = read_records('movierequests-%s.txt' % form.year, 5)
else:
    records = read_records('movierequests.txt', 5)

# Read the movie request messages, attaching reply messages to their requests.

requests = []
replies = {}
for id, date, name, movie, comment in records:
    date, time = parse_date(date.split()[0]), date.split()[1]
    if id[:1] == '>':
        replies[id[1:]] = replies.get(id[1:], [])
        replies[id[1:]].append((date, time, name, movie, comment))
    else:
        requests.append((id, date, time, name, movie, comment))
        replies[id] = []
requests.reverse()

# Construct the table rows for the movie request message board.

selector = ''
rows = []
parity = 'even'
for id, date, time, name, movie, comment in requests:
    if not form.year:
        rbutton = input(id=id, name='id', type='radio', value=id)
        rlabel = label('add a reply here', for_=id)
        selector = trt(td(div(rbutton, rlabel, c='selector'), colspan=2))
    parity = (parity == 'even') and 'odd' or 'even'
    rows.append(trt(format_request((date, time, name, movie, comment))[1],
                    td(table(map(format_request, replies[id]), selector, c='comment'),
                       c='replies'), c=parity))
if form.year:
    rows.append('<script>disabled = 1</script>')

# Display the page.

prologue('Kingman Hall: Movie Requests Board', 'style.css')
write_template('movierequests.html', notes=table(rows, c='notes'))
epilogue()
