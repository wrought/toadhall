#!/usr/bin/env python

from utils import *
import random

respondents = 0
for line in readlines('voc-members.txt'):
    if line.strip() != 'comment-only':
        respondents += 1

managers = [('House Manager', '9/16 rent plus 5 hours/week', 'Sonja'),
            ('Kitchen Manager', '100% rent plus 5 hours/week', 'Gaby'),
            ('Workshift Manager', '9/16 rent plus 5 hours/week', 'Erin'),
            ('Maintenance Manager', '9/16 rent plus 5 hours/week', 'Daniel'),
            ('Social Manager', '2.5 hours/week', 'David'),
            ('Social Manager', '2.5 hours/week', 'Yana'),
            ('Waste Reduction Manager', '5 hours/week', 'Lisa'),
            ('Garden Manager', '5 hours/week', 'Beaver'),
            ('Board Representative', '5 hours/week', 'Kate'),
            ('Network Manager', '3 hours/week', 'Jonathan'),
            ('Vice President', '3 hours/week', 'Brian C.'),
            ('President', '5 hours/week', 'Ping')]

managerdict = {}
responses = {'comp': {}, 'text': {}}
for position, comp, name in managers:
    nameid = name.strip().lower().replace(' ', '-').replace('.', '')
    managerdict[nameid] = position, comp, name
    responses['comp'][nameid] = []
    responses['text'][nameid] = []

for line in readlines('voc-results.txt'):
    if ':' in line:
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        nameid, type = key.rsplit('-', 1)
        position, comp, name = managerdict[nameid]
        responses[type][nameid].append(value)

write('Content-Type: text/html; charset=utf-8\n\n')
write('''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd"><html>''')
write('<head><link rel="stylesheet" href="style.css"></head>')
write('<body class="vocs">')
write(h1('VOC Results'))

for position, comp, name in managers:
    nameid = name.strip().lower().replace(' ', '-').replace('.', '')
    write(h2('%s (%s, %s)' % (name, position, comp)))
    headings = []
    counts = []
    for value in '80% 90% 100% 110% Abstain'.split():
        key = value.lower().replace('%', '')
        headings.append(th(value))
        votes = responses['comp'][nameid].count(key)
        counts.append(td('%s vote%s' % (votes, votes != 1 and 's' or '')))
    write(table(tr(headings), tr(counts), c='vocs'))
    print '<ul>'
    random.shuffle(responses['text'][nameid])
    for text in responses['text'][nameid]:
        write(li(esc(text).replace('\t', '<br>')))
    print '</ul>'
