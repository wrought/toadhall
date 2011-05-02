#!/usr/bin/env python

import os, time, re, csv
from utils import *
from fastcgi import form

# Put the member name of the Workshift Manager and a witty saying here.

WORKSHIFT_MANAGER = 'anna'
WORKSHIFT_MANAGER_SLOGAN = 'finds ghosts tastier than dots'

# These are the files used to produce a report.  You can edit these filenames.

MEMBER_FILE = '/home/workshift/Member Information.txt'
WORKSHIFT_FILE = '/home/workshift/Workshift Information.txt'
WEEK_FILE = '/home/workshift/Weeks.txt'
HOUR_FILE = '/home/workshift/Hours.txt'
BATHROOM_FILE = '/home/workshift/Bathroom Shifts.txt'
HUMOUR_FILE = '/home/workshift/Humor Shifts.txt'

# Don't change anything below this point.

USED_COLUMNS = {
# Here are the columns that must be present in each file.  The columns may
# appear in the file in any order and capitalization doesn't matter.
#
# File              Columns Used
  MEMBER_FILE:      "member, first, last, inactive, week 1, week 2", # etc.
  WORKSHIFT_FILE:   "win, workshift, day, hours, description, in use",
  HOUR_FILE:        "week, member, hours, type, win",
  WEEK_FILE:        "week, start date, fine week",
  BATHROOM_FILE:    "member, floor, start date, end date, performed",
  HUMOUR_FILE:      "member, type, date, performed"
}

class Item(dict):
    def __getattr__(self, name):
        return self[name]

def field_name(heading):
    """Normalize the name of a table field."""
    heading = re.sub('\\W', ' ', heading)
    heading = '_'.join(heading.split())
    return heading.lower()

def read_table(path, key=None, **parsers):
    """Read a CSV file that has column headings on the first line."""
    if not os.path.isfile(path):
        return {}
    reader = csv.reader(open(path))
    try:
        headings = [field_name(heading) for heading in reader.next()]
    except StopIteration:
        return {}
    records = {}
    count = 0
    for record in reader:
        item = Item()
        for name, value in zip(headings, record):
            if name in parsers:
                try:
                    value = parsers[name](value)
                except:
                    value = None
                    problems += [[
    'Row %d of the %s table has an invalid %r field (the whole row is %r).' %
    (count + 1, os.path.splitext(os.path.basename(path))[0], name, record)]]
            item[name] = value
        records[item.get(key, count)] = item
        count += 1
    return records

def select(table, **conditions):
    """Get all the items in a table that match the given criteria."""
    results = []
    for item in table.values():
        match = 1
        for name in conditions:
            if callable(conditions[name]):
                if not conditions[name](item[name]):
                    match = 0
            elif item[name] != conditions[name]:
                match = 0
        if match:
            results.append(item)
    return results

def last_full_week(date, weeks):
    """Determine the last full week that ended before a given date."""
    lastweek = -1
    for week in sorted(weeks.keys()):
        if weeks[week].start_date + 6 < date:
            lastweek = week
    return lastweek

# Various data conversion functions for use with read_table.

def int_or_blank(text):
    return text and int(text) or 0

def float_or_blank(text):
    return text and float(text) or 0

date = parse_date

def day(text):
    text = text.strip().capitalize()
    try:
        return daynames.index(text)
    except ValueError:
        return text

def description(text):
    """Convert the workshift description text into HTML."""
    text = esc(text)
    text = re.sub(r'\n--\s', '\n\n', '\n' + text)
    text = re.sub(r'\n[\?\x95]\s', '\n<li>', '\n' + text)
    text = re.sub(r'((\n<li>.*)+)\n*', r'<ul>\1</ul>', '\n' + text)
    text = text.replace('\x85', '&mdash;')
    text = text.replace('\x92', '&#8217;')
    text = text.replace('\x93', '&#8220;')
    text = text.replace('\x94', '&#8221;')
    text = text.replace('\xba', '&#176;')
    text = re.sub(r'\n*<ul>\n*', '<ul>', text)
    text = re.sub(r'\n*<li>\n*', '<li>', text)
    text = re.sub(r'\n\s*\n(\s*\n)+', '\n<p>', text)
    text = text.strip().replace('\n', br)
    return text

# Sections of the display.

def get_workshift_descriptions():
    """Return a dictionary that maps workshift names to descriptions."""
    descriptions = {}
    for win in workshifts:
        shift = workshifts[win]
        name = shift.workshift
        if shift.in_use:
            descriptions[name] = descriptions.get(name, '') + shift.description
    return descriptions

def make_id(name):
    """Generate an HTML fragment identifier from a workshift name."""
    name = re.sub(r'\W', ' ', name.lower())
    return '_'.join(name.split())

def workshift_menu(linkbase=''):
    """Produce the menu of workshifts with links to their descriptions."""
    descriptions = get_workshift_descriptions()
    return multicolumn([
        link(linkbase + '#%s' % make_id(name), name)
        for name in sorted(descriptions.keys())], c='menu')

def workshift_descriptions():
    """Produce the page of workshift descriptions."""
    result = []
    descriptions = get_workshift_descriptions()
    for name in sorted(descriptions.keys()):
        title = div(a(name, name=make_id(name)), c='title')
        description = descriptions[name].strip()
        desc = div(description or '(no description)', c='description')
        result += div(title, desc, c='workshift')
    return result

def heading_box(heading, *content):
    return [div(heading, c='heading'), div(content, c='content')]

def format_week_number(number):
    """Format the display of a week number."""
    return table(tr(td('week', nbsp), td(number, c='number')), c='week')

def format_date(date, message=''):
    return div(message, span(date.format('%dddd'), c='weekday'), br,
               date.format('%mmmm %d'), c='datelines')

def next_fine_box(weeks):
    week = last_full_week(today, weeks) + 1
    while week < len(weeks) and not weeks[week].fine_week:
        week += 1
    if week >= len(weeks):
        return ''
    finedate = weeks[week].start_date + 6
    c = (finedate < today + 7) and 'soon' or ''
    return heading_box(h2('Next fine date'),
                       div(format_week_number(week),
                           format_date(finedate), c=c))

def logo():
    return h1(link('workshifts.cgi',
                   [span(c, c='w%d' % i) for i, c in enumerate('Workshifts')]),
              c='workshift')
    return div(link('workshifts.cgi', img('workshift.png')), c='logo')

def heading():
    current_date_box = heading_box(h2('Today'),
                                   format_week_number(this_week),
                                   format_date(today))
    last_update_box = heading_box(h2('Last updated'),
                                  format_week_number(last_update_week),
                                  format_date(last_update_date, 'ended '))
    cells = [td(logo(), c='logo'),
             td(last_update_box, c='datebox'),
             td(nbsp),
             td(current_date_box, c='datebox')]
    next_fine = next_fine_box(weeks)
    if next_fine:
        cells += [td(nbsp), td(next_fine, c='datebox')]
    return tablew(tr(cells, c='pageheading'))

def bathroom_cell((member, performed)):
    return td(member, c=performed and 'up' or 'down')

def bathroom_row_class(date):
    if date >= today:
        if date <= today + 7:
            return 'soon future'
        return 'future'
    if date > last_update_date:
        return 'pending'
    return ''

def bathroom_table(min_date=None, max_date=None):
    rows = [tr(th(''), th('1st floor'), th('2nd floor'), th('3rd floor'))]
    schedule = {}
    for shift in bathrooms.values():
        key = (shift.start_date, shift.end_date)
        if key not in schedule:
            schedule[key] = ['', '', '', '']
        schedule[key][shift.floor] = (shift.member, shift.performed)
    for start, end in sorted(schedule.keys()):
        if min_date and start < min_date:
            continue
        if max_date and end > max_date:
            continue
        row = schedule[(start, end)]
        format = start.month == end.month and '%ddd %d' or '%ddd %d %mmm'
        range = [start.format(format), ndash, end.format('%ddd %d %mmm')]
        rows.append(tr(td(range, c='date'),
                       bathroom_cell(row[1]),
                       bathroom_cell(row[2]),
                       bathroom_cell(row[3]),
                       c=bathroom_row_class(end)))
    return table(tr(rows), c='bathroom')

def humour_table(min_date=None, max_date=None):
    rows = [tr(th(''), th('Meep &amp; Swop'),
               th('Evening Pots'), th('Evening Pots'))]
    schedule = {}
    for shift in humours.values():
        date = shift.date
        if 'mop' in shift.type.lower():
            type = 'mop'
        elif 'pots' in shift.type.lower():
            type = 'pots'
        else:
            problems += [['There is a humour shift on %s with the type %r' %
                          (shift.date, shift.type), ' (the type should be ',
                          "'Sweep and Mop' or 'Evening Pots')."]]
            continue
        if date not in schedule:
            schedule[date] = {}
        while type in schedule[date]:
            type += '+'
        if type not in ['mop', 'pots', 'pots+']:
            problems += [['There seem to be too many humour shifts ',
                          'of the same type on %s.' % date]]
        schedule[date][type] = (shift.member, shift.performed)
    for date in sorted(schedule.keys()):
        if min_date and date < min_date:
            continue
        if max_date and date > max_date:
            continue
        row = schedule[date]
        rows.append(tr(td(date.format('%ddd %d %mmm'), c='date'),
                       bathroom_cell(row['mop']),
                       bathroom_cell(row['pots']),
                       bathroom_cell(row['pots+']),
                       c=bathroom_row_class(date)))
    return table(tr(rows), c='humour')

# Main program starts here.

problems = []

# Display an explanation of any errors that occurred.
def show_problems():
    write(div(strong('Excuse me... the database looks a bit odd.'),
              " (If this doesn't match what you see in the database,",
              " be sure to export <strong>all</strong> the tables.)", br,
              br.join(map(flatten, problems)), c='problems'))

hook = cgitb.Hook()
def excepthook(*args):
    prologue('Kingman Hall: Workshifts', 'style.css')
    if problems:
        show_problems()
    hook(*args)

sys.excepthook = excepthook

for filename, columns in USED_COLUMNS.items():
    try:
        records = read_table(filename)
    except csv.Error, err:
        problems += [['The file ', filename, ' has a bad format: %s.' % err]]
        continue
    if records:
        for column in columns.split(','):
            if field_name(column) not in records[0]:
                problems += [['The file ', filename,
                    ' is missing a column named ', strong(column), '.']]
    else:
        problems += [['There are no records in the file ', filename, '.']]

# Read in tables from the data files from the workshift database.

week_fields = dict([('week_%d' % i, float_or_blank) for i in range(20)])

members = read_table(MEMBER_FILE, 'member', inactive=int, **week_fields)
workshifts = read_table(WORKSHIFT_FILE, 'win', win=int, day=day,
                        hours=float, description=description, in_use=int)
hours = read_table(HOUR_FILE, week=int, hours=float, win=int)
weeks = read_table(WEEK_FILE, 'week', week=int, start_date=date, fine_week=int)
bathrooms = read_table(BATHROOM_FILE, start_date=date, end_date=date,
                       floor=int, performed=int)
humours = read_table(HUMOUR_FILE, date=date, performed=int)

# Look for problems in the data.

for name, data in [('Hours', hours),
                   ('Bathroom Shifts', bathrooms),
                   ('Humour Shifts', humours)]:
    for key, record in data.items():
        if record['member'].strip() and record['member'] not in members:
            problems += [[
    'Row %r of the %s table has the member name %r,' %
    (key, name, record['member']),
    ' which is not listed as a member in the Members table',
    ' (the whole row is %s).' % repr(record.values())]]

for key, record in hours.items():
    if record['win'] not in workshifts:
        problems += [[
    'Row %r of the Hours table has the WIN %r,' % (key, record['win']),
    ' which is not listed as a WIN in the Workshifts table',
    ' (the whole row is %s).' % repr(record.values())]]

# Figure out important dates.

if hours:
    last_update_week = max([item.get('week', 1) for item in hours.values()])
else:
    last_update_week = 0
today = get_date()
this_week = last_full_week(today, weeks) + 1
last_update_date = weeks[last_update_week].start_date + 6

def output_page(title, *contents):
    prologue('Kingman Hall: %s' % title, 'style.css')
    if problems:
        show_problems()
    write(contents)
    epilogue()

if form.member in members:
    # Show the workshift history for a specific member.

    member = form.member
    mrow = members[member]
    total = 0
    rows = [tr(td(colspan=5), th('running total'))]

    for week in range(last_update_week + 1):
        owed = mrow.get('week_%d' % week, 0)
        mhours = select(hours, member=member, week=week)
        mhours.sort(key=lambda r: r.win)
        start = weeks[week].start_date
        daterange = [start.format('%mmm %d'), ' to ',
                     (start + 6).format('%mmm %d')]
        rows += tr(td('Week %d' % week, c='week'),
                   td(daterange, colspan=2),
                   tdr('owed'),
                   tdr('%.2f' % owed),
                   c='section')
        total -= owed
        wtotal = 0
        for row in mhours:
            type = row.type != 'Standard' and row.type.lower() or ''
            rowclass = row.hours >= 0 and 'up' or 'down'
            if row.win in workshifts:
                shift = workshifts[row.win]
                try:
                    weekday = daynames[shift.day]
                except:
                    weekday = ''
                workshift = shift.workshift
            else:
                weekday = 'Uh-oh!'
                workshift = '%d is an invalid WIN.' % row.win
                rowclass = 'error'
            rows += tr(td(),
                       td(weekday),
                       td(workshift),
                       tdr(type),
                       tdr('%.2f' % row.hours),
#                       td(colspan=2, c='section'),
                       c=rowclass)
            total += row.hours
            wtotal += row.hours

        updown = total >= 0 and 'up' or 'down'
        c = (week == last_update_week) and 'final' or ''
        rows += tr(td(),
                   td(mhours and ' ' or '(no hours recorded)', colspan=2),
                   tdr('total', c='total'),
                   tdr('%.2f' % wtotal, c='total'),
                   tdr(updown + ' %.2f' % abs(total), c='' + updown), c=c)

    output_page('Workshifts for ' + member,
                heading(), h1(member), table(rows, c='workshifts'))

elif form.descriptions:
    # Show all the workshift descriptions.

    output_page('Workshift Descriptions', heading(), p,
                'Select a workshift to see its description.',
                workshift_menu(), workshift_descriptions())

elif form.humour:
    # Show the schedule of bathroom and humour shifts.

    output_page(
        'Bathroom and Humour Shifts', heading(), p,
        'Note: ', span('Green', c='up'), ' means done. ',
        span('Red', c='down'), ' means blown. ',
        span('Yellow', c='pending'), ' means not entered yet.',
        tablew(tr(td(h2('Bathroom Shifts'), bathroom_table(), c='bathroom'),
                  td(h2('Humour Shifts'), humour_table(), c='humour')),
               c='bathroom-humour'))

else:
    # Show a menu of members and a menu of workshifts.

    items = []
    for member in sorted(members.keys()):
        mrow = members[member]
        mhours = select(hours, member=member,
                        week=lambda w: w <= last_update_week)
        worked = sum([row.hours for row in mhours])
        owed = sum([mrow.get('week_%d' % i, 0)
                   for i in range(last_update_week + 1)])
        if not mrow.inactive:
            url = 'workshifts.cgi?member=%s' % urlquote(member)
            if member == WORKSHIFT_MANAGER:
                updown = WORKSHIFT_MANAGER_SLOGAN
            elif worked >= owed:
                updown = '<span class=up>up %g</span>' % (worked - owed)
            else:
                updown = '<span class=down>down %g</span>' % (owed - worked)
                if (owed - worked) >= 20:
                    updown += ' <strong>&#8805; 20!</strong>'
                elif (owed - worked) >= 15:
                    updown += ' <strong>&#8805; 15!</strong>'
            items.append([link(url, member), ': ', updown])

    output_page(
        'Workshifts', heading(), p,
        'Current bathroom shifts and humour shifts (or ',
        link('workshifts.cgi?humour=1', 'see the whole schedule'), '):',
        tablew(tr(td(bathroom_table(min_date=today, max_date=today + 7),
                     c='bathroom'),
                  td(humour_table(min_date=today, max_date=today + 7),
                     c='humour')),
                  c='bathroom-humour recent menu'),
        p, 'Select one of the active members to see details.',
        multicolumn(items, 4, c='menu'),
        p, 'Select a workshift to see its description.',
        workshift_menu('workshifts.cgi?descriptions=1'))
