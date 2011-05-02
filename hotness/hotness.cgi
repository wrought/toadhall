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

    sample = {'mf': 67, 'f': 32, 'm': 35}[form.object]
    try:
        number = float(form.number)
    except:
        quit('Please enter a valid number.')

    if number > sample:
        quit("There aren't that many fish in the sea!")

    file = open('hotness.txt', 'a')
    file.write('%d\tdo\t%s\t%s\t%s\n' %
               (time.time(), form.subject, form.object, form.number))
    file.close()
    print 'Location: index.cgi\n'

else:
    quotients, counts = get_hotness('do', {'m': 35, 'f': 32})
    hq = percentage(quotients[('any', 'any')])
    fhq = percentage(quotients[('any', 'f')])
    mfhq = percentage(quotients[('m', 'f')])
    ffhq = percentage(quotients[('f', 'f')])
    mhq = percentage(quotients[('any', 'm')])
    fmhq = percentage(quotients[('f', 'm')])
    mmhq = percentage(quotients[('m', 'm')])
    n = sum(counts.values())

    prologue('Kingman Hall: Hotness Quotient', 'style.css')
    write_template('hotness.html', hq=hq, fhq=fhq, mhq=mhq,
                   mfhq=mfhq, ffhq=ffhq, fmhq=fmhq, mmhq=mmhq, n=n)
    epilogue()
