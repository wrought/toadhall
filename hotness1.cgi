#!/usr/bin/env python

from utils import *
from fastcgi import form
import sys, time, os

def quit(message):
    prologue('Kingman Hall: Hotness Quotient', 'style.css')
    write(message)
    sys.exit()

if form.submit:
    if form.subject not in ['m', 'f']:
        quit('Please choose a gender.')

    if form.object not in ['m', 'f', 'mf']:
        quit('Please choose a gender preference.')

    sample = {'mf': 68, 'f': 33, 'm': 35}[form.object]
    try:
        number = float(form.number)
    except:
        quit('Please enter a valid number.')

    if number > sample:
        quit("There aren't that many fish in the sea!")

    try:
        makeout = float(form.makeout)
    except:
        quit('Please enter a valid number.')

    if makeout > sample:
        quit("There aren't that many frogs in the pond!")

    file = open('hotness.txt', 'a')
    file.write('%d\tdo\t%s\t%s\t%s\n' %
               (time.time(), form.subject, form.object, form.number))
    file.write('%d\tmakeout\t%s\t%s\t%s\n' %
               (time.time(), form.subject, form.object, form.makeout))
    file.close()
    print 'Location: index.cgi\n'

else:
    quotients, counts = get_hotness('do', {'m': 35, 'f': 33})
    hq = percentage(quotients[('any', 'any')])
    fhq = percentage(quotients[('any', 'f')])
    mfhq = percentage(quotients[('m', 'f')])
    ffhq = percentage(quotients[('f', 'f')])
    mhq = percentage(quotients[('any', 'm')])
    fmhq = percentage(quotients[('f', 'm')])
    mmhq = percentage(quotients[('m', 'm')])
    n = sum(counts.values())

    quotients, counts = get_hotness('makeout', {'m': 35, 'f': 33})
    mk = percentage(quotients[('any', 'any')])
    fmk = percentage(quotients[('any', 'f')])
    mfmk = percentage(quotients[('m', 'f')])
    ffmk = percentage(quotients[('f', 'f')])
    mmk = percentage(quotients[('any', 'm')])
    fmmk = percentage(quotients[('f', 'm')])
    mmmk = percentage(quotients[('m', 'm')])

    prologue('Kingman Hall: Hotness Quotient', 'style.css')
    write_template('hotness.html', hq=hq, fhq=fhq, mhq=mhq,
                   mfhq=mfhq, ffhq=ffhq, fmhq=fmhq, mmhq=mmhq, 
                   mk=mk, fmk=mk, mmk=mmk, mfmk=mfmk, ffmk=ffmk,
                   fmmk=fmmk, mmmk=mmmk, n=n)
    epilogue()
