#!/usr/bin/env python

from utils import *
import random

respondents = 0
for line in read_lines('voc-members.txt'):
    if line.strip() != 'comment-only':
        respondents += 1

managers = [('House Manager', '9/16 rent plus 5 hours/week', 'Tony'),
            ('Kitchen Manager', '100% rent plus 5 hours/week', 'Gaby'),
            ('Workshift Manager', '9/16 rent plus 5 hours/week', 'Madelyn'),
            ('Maintenance Manager', '9/16 rent plus 5 hours/week', 'Beaver'),
            ('Social Manager', '2.5 hours/week', 'Justyna'),
            ('Social Manager', '2.5 hours/week', 'Adriana'),
            ('Social Managers', 'both together', 'Social Managers'),
            ('President', '5 hours/week', 'Ping'),
            ('Vice President', '3 hours/week', 'Brian'),
            ('Board Representative', '5 hours/week', 'Kate'),
            ('Waste Reduction Manager', '5 hours/week', 'Lisa'),
            ('Garden Manager', '5 hours/week', 'Grace'),
            ('Network Manager', '3 hours/week', 'Jonathan')]

managerdict = {}
responses = {'vote': {}, 'text': {}}
for position, comp, name in managers:
    nameid = name.strip().lower().replace(' ', '-').replace('.', '')
    managerdict[nameid] = position, comp, name
    responses['vote'][nameid] = []
    responses['text'][nameid] = []

for line in read_lines('voc-results.txt'):
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
    if nameid == 'social-managers':
        write(h2('%s (%s)' % (name, comp), id=nameid))
    else:
        write(h2('%s (%s, %s)' % (name, position, comp), id=nameid))
    headings = []
    counts = []
    for value in '80% 90% 100% 110% Abstain'.split():
        key = value.lower().replace('%', '')
        headings.append(th(value))
        votes = responses['vote'][nameid].count(key)
        counts.append(td('%s vote%s' % (votes, votes != 1 and 's' or '')))
    if nameid != 'social-managers':
        write(table(tr(headings), tr(counts), c='vocs'))
    print '<ul>'
    random.shuffle(responses['text'][nameid])
    for text in responses['text'][nameid]:
        write(li(esc(text).replace('\t', '<br>')))
    print '</ul>'
