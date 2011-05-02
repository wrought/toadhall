#!/usr/bin/env python

from utils import *
from fastcgi import form
import time, os

members = ['1A Gaby', '1B Adrienne', '1C Nick', '1D Sonja', '1E Elliot',
           '1F Maya', '1F Claire', '1G Tram', '1G Lisa',
           '1H Ryan B.', '1H Geoff',
           '2A Grace', '2A Daniel', '2B Navek', '2B Aaron',
           '2C Justyna', '2C Madelyn', '2D Kye', '2D Dianna',
           '2E Mike', '2E Brian C.', '2E Beaver',
           '2F Daphne', '2G Daisy', '2H Jordan', '2I David', '2I Robb',
           '2J Anthony', '2J Joe', '2K Erin', '2K Zoe', '2L Phil', '2L Josh',
           '3A Kate', '3B Rachel', '3B Christina', '3C Yana', '3C Sophie',
           '3D Jonathan', '3D Nate', '3E Hanna', '3E Meaghan',
           '3F Melina', '3F Adriana', '3G Molly', '3G Lana',
           '3H Ping', '3I Ryan D.', '3J Galen', '3J Brian G.']

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

disabled = {}
for line in readlines('voc-members.txt'):
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
def managerform((position, comp, name)):
    global y
    nameid = name.strip().lower().replace(' ', '-').replace('.', '')
    buttons = []
    for option in '80% 90% 100% 110% Abstain'.split():
        val = option.replace('%', '').lower()
        y += 1
        buttons.append(div(input(type='radio', name=nameid + '-comp',
                                 value=val, id='comp-%d' % y),
                           label(option, for_='comp-%d' % y),
                           id='compdiv-%d' % y))
    return div(position, ' compensation is ', comp, '.', br,
               strong(name), ' deserves this much of the comp:', buttons, br,
               table(tr(td('Comments:', valign='top'),
                        td(textarea(name=nameid + '-text', rows=5, cols=60))),
                     c='textarea'),
               c='manager', id='manager-%d' % y)

if form.submit:
    if not form.member:
        prologue('Kingman Hall: Votes of Confidence', 'style.css')
        write("You didn't select your name. Please go back and fill it in.")
        raise SystemExit

    results = '\n'
    for (position, comp, name) in managers:
        nameid = name.strip().lower().replace(' ', '-').replace('.', '')
        compfield = nameid + '-comp'
        textfield = nameid + '-text'
        if form.member != 'comment-only':
            if compfield not in form:
                prologue('Kingman Hall: Votes of Confidence', 'style.css')
                write("You didn't choose a compensation amount for %s (%s). "
                      % (name, position))
                write('Please go back and fill it in.')
                raise SystemExit
            results += compfield + ': ' + form[compfield] + '\n'
        if textfield in form and form[textfield]:
            text = form[textfield].replace('\t', ' ').replace('\r\n', '\n'
                 ).replace('\r', '\n').replace('\n', '\t')
            results += textfield + ': ' + text + '\n'
        
    file = open('voc-members.txt', 'a')
    file.write(form.member + '\n')
    file.close()
    file = open('voc-results.txt', 'a')
    file.write(results)
    file.close()
    prologue('Kingman Hall: Votes of Confidence', 'style.css')
    write(p, 'Thank you.  Your answers have been recorded.')
    write(p, 'You can only vote once for manager compensation, ',
             'but you can resubmit the form to add more comments if you want.')
else:
    cells = []
    names = members[:]
    while names:
        cells.append([memberselect(name) for name in names[:11]])
        names[:11] = []
    commentonly = [input(type='radio', name='member', value='comment-only',
                         id='comment-only', onclick='update()'),
                   label("I've already cast my votes ",
                         "and I just want to add some comments.",
                         for_='comment-only')]
    n = len(cells)
    membertable = table(tr(td('Choose your name from this list:', colspan=n)),
                        tr([td(cell) for cell in cells]),
                        tr(td(commentonly, colspan=n)), c='members')
    managerfields = [managerform(manager) for manager in managers]

    prologue('Kingman Hall: Votes of Confidence', 'style.css')
    html = readfile('vocs.html')
    write(subst(html, members=membertable, managers=managerfields))
