#!/usr/bin/env python

from utils import *
from fastcgi import form
import time, os

keys = 'id first last room status phone e-mail aim yim offers interests'.split()

def row(member, room=0):
    """Format one row of the member listing table."""

    name_link = link('members.cgi?id=%s' % member['id'],
                     member['first'], ' ', member['last'])
    return tr(td(name_link),
              room and td(member['room']) or '',
              td(member['phone']),
              td(member['e-mail']))

def fix_text(text):
    """Convert free-form text to make it safe to store in a record file."""
    return text.replace('\t', ' ').replace('\r\n', '\n').replace('\n', '\t')

form.id = form.id and int(form.id)

if form.update:
    # Update a member record with the submitted edits.

    if not form.id:
        form.id = next_member_id()
    member = get_member(form.id)
    for key in keys:
        member[key] = form[key]
    member['offers'] = fix_text(form['offers'])
    member['interests'] = fix_text(form['interests'])
    put_member(member, time.time(), os.environ['REMOTE_ADDR'])

    # Return to the edited member's detail page.

    print 'Location: members.cgi?id=%d\n' % form.id

elif not form.edit and not form.id:
    # Get the records for all the members.

    members = get_members()

    # Sort them according to the selected sort key.

    sortkey = form.sort or 'last'
    def compare(ma, mb):
        return cmp([ma[key].lower() for key in [sortkey, 'last', 'first']],
                   [mb[key].lower() for key in [sortkey, 'last', 'first']])
    members.sort(compare)

    # Separate the member list out into three lists.

    residents = filter(lambda m: m['status'] == 'resident', members)
    boarders = filter(lambda m: m['status'] == 'boarder', members)
    oldmembers = filter(lambda m: m['status'] == 'oldmember', members)

    # Write out the member listing page.

    prologue('Kingman Hall: Members', 'style.css')
    write_template('members.html',
                   residents=[row(m, room=1) for m in residents],
                   boarders=[row(m, room=0) for m in boarders],
                   oldmembers=[row(m, room=0) for m in oldmembers])
    epilogue()

else:
    # Get the record for the selected member.

    if form.id:
        member = get_member(form.id)
        member['name'] = member['first'] + ' ' + member['last']
    else:
        member = Member()
        member['name'] = 'Add a Member'
    for key in keys:
        member[key] = member[key] or ''

    # Convert and format the record fields for display.

    member_display = dict([(key, esc(str(member[key]))) for key in member])
    for value in 'resident boarder oldmember'.split():
        member_display['status_' + value] = (
            member['status'] == value and 'checked' or '')
    member_display['status_name'] = {
        'resident': 'Current Resident',
        'boarder': 'Current Boarder',
        'oldmember': 'Past Member'}.get(member['status'], '')

    # Write out the page for the member record.

    prologue('Kingman Hall: %s' % member['name'], 'style.css')
    if form.edit:
        write_template('member-edit.html', **member_display)
    else:
        write_template('member-view.html', **member_display)
    epilogue()
