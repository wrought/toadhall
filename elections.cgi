#!/usr/bin/env python

from utils import *
from fastcgi import form
import time, os

members = ['Aaron', 'Adina', 'Adrienne', 'Amy', 'Andre', 'Andy', 'Anna',
           'Athena', 'Barbara', 'Laura B', 'Caitlyn', 'Catherine',
           'Chris', 'Daisy', 'Daniel', 'Daphne', 'David B', 'Dennis',
           'Elliot', 'Emanuel', 'Galen', 'Geoff', 'Grace', 'Griffin',
           'Hanna', 'Jessica', 'Jonathan', 'Jordan', 'Josh', 'Julien',
           'Justyna', 'David K', 'Kosta', 'Lisa', 'Madelyn', 'Martha',
           'Mary', 'Max', 'Michelle', 'Navid', 'Nick', 'Ping',
           'Rebecca', 'David R', 'Rohit', 'Sarah', 'Shannon', 'Steven',
           'Tim', 'Tony', 'Tracy', 'Willie', 'Yelena', 'Zhongxia']
members.sort()

managers = [('Kitchen Manager', '100% rent plus 5 hours/week',
             ['Rohit', 'Dennis']),
           ]

disabled = {}
for line in read_lines('elections-members.txt'):
    disabled[line.strip()] = 1

x = 0
def memberselect(name):
    global x
    x += 1
    dis = disabled.get(name, None)
    return div(input(type='radio', name='member', value=name, disabled=dis,
                     id='radio-%d' % x, onclick='update(%r)' % x),
               label(name, for_='radio-%d' % x),
               id='namediv-%d' % x, c=dis and 'disabled' or None)

y = 0
def managerform((position, comp, candidates)):
    global y
    rows = []
    for candidate in candidates + ['None of the above']:
        id = position + '.' + candidate.replace('.', '')
        id = id.lower().replace(' ', '-')
        rows.append(tr(td(input(type='text', size='3', name=id, id=id)),
                       td(label(nbsp, candidate, for_=id))))
    fragment = position.split()[0].lower()
    linkposition = link('duties.html#' + fragment, position)
    return div(h2(linkposition, ' (%s)' % comp), table(rows), c='manager')

closed = 1

if form.submit:
    if closed:
        prologue('Kingman Hall: House Elections', 'style.css')
        write("The election is closed.  No more votes can be accepted.") 
        raise SystemExit

    if not form.member:
        prologue('Kingman Hall: House Elections', 'style.css')
        write("You didn't select your name. Please go back and select it.")
        raise SystemExit

    if form.member in disabled:
        prologue('Kingman Hall: House Elections', 'style.css')
        write("You already voted, so you can't vote again.")
        raise SystemExit

    results = '\n'
    for (position, comp, candidates) in managers:
        for candidate in candidates + ['None of the above']:
            if form[id]:
                try:
                    value = int(form[id].strip())
                    assert 0 < value < 100
                except:
                    prologue('Kingman Hall: House Elections', 'style.css')
                    write('Each rank must be a number from 1 to 99.')
                    raise SystemExit
                
            id = position + '.' + candidate.replace('.', '')
            id = id.lower().replace(' ', '-')
            results += id + ': ' + form[id] + '\n'
        
    file = open('elections-members.txt', 'a')
    file.write(form.member + '\n')
    file.close()
    file = open('elections-results.txt', 'a')
    file.write(results)
    file.close()
    prologue('Kingman Hall: House Elections', 'style.css')
    write(p, 'Thank you.  Your answers have been recorded.')
else:
    cells = []
    names = members[:]
    while names:
        floor = [name for name in names if name[0] == names[0][0]]
        n = min(11, len(floor))
        n = 11
        cells.append([memberselect(name) for name in names[:n]])
        names[:n] = []
    membertable = table(tr(td('Choose your name from this list:', colspan=n)),
                        tr([td(cell) for cell in cells]), c='members')
    managerfields = [managerform(manager) for manager in managers]

    prologue('Kingman Hall: House Elections', 'style.css')
    write_template('elections.html',
                   members=membertable, managers=managerfields)
