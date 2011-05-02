#!/usr/bin/python

from utils import *
from fastcgi import form
import os

pages_per_pixel = 7.0
days = int(form.days or 30)

records = get_toner_records(days*3)
dates = records.keys()
dates.sort()
rows = [tr(th('Date', c='date'),
           th(table(tr(th('Pages Printed', c='printed'),
                       th('Pages Remaining', c='remaining'))), colspan=3),
           th('Toner Left', c='toner', colspan=2))]

pages = []
for date in dates[-days:]:
    record = records[date]
    printed = int(record.get('pages_printed', 0) or 0)
    remaining = int(record.get('pages_remaining', 0) or 0)
    pages.append(printed + remaining)

for date in dates[-days:]:
    record = records[date]
    printed = int(record.get('pages_printed', 0) or 0)
    remaining = int(record.get('pages_remaining', 0) or 0)
    pwidth = int(printed/pages_per_pixel + 0.5)
    rwidth = int((printed + remaining)/pages_per_pixel + 0.5) - pwidth
    twidth = int(max(pages)/pages_per_pixel + 0.5)
    try:
        toner = int(record.get('black_cartridge', 0) or 0)
    except:
        toner = 0
    bars = table(tr(td(width=pwidth, c='printedbar'),
                    td(width=rwidth, c='remainingbar'),
                    td(width=twidth - pwidth - rwidth)))
    tonerbars = table(tr(td(width=toner, c='tonerbar'),
                         td(width=100-toner, c='tonerusedbar')))
    rows += tr(td(date, c='date'), td(printed, c='printed'),
               td(bars, c='bars'), td(remaining, c='remaining'),
               td(toner, '%', c='toner'), td(tonerbars, c='tonerbars'))

# Display the page.

prologue('Kingman Hall: Printer Usage', 'style.css')
write_template('printer.html', chart=table(rows, c='printer'))
epilogue()
