#!/usr/bin/python

from utils import *
from fastcgi import form, request
import os, time, re; local = time.localtime()

url, key, addr, city = form.url, form.key, form.addr, form.city
query = action = ''
if form.action:
    action = form.action.lower().split()[0]
elif form.key:
    action = 'google'
if ',' not in city:
    city += ', CA'

if not url:
    url = os.path.dirname(request) + '/'

# if action == 'url':
#     if '.' not in url: url += '.com'
#     if re.match('http:// *[a-z]+://', url): url = url[7:].strip()
#     if not re.match('[a-z]+://', url): url = 'http://' + url
if action == 'google':
    url = 'http://google.com/search'
    query = form_encode(q=key)
if action == 'wikipedia':
    url = 'http://en.wikipedia.org/wiki/Special:Search'
    query = form_encode(search=key)
if action == 'dictionary':
    # url = 'http://dictionary.com/cgi-bin/dict.pl'
    # query = pairs(term=q)
    # url = 'http://www.m-w.com/cgi-bin/dictionary'
    # query = form_encode(va=key, book='Dictionary')
    url = 'http://www.answers.com/main/ntquery'
    query = form_encode(s=key)
if action == 'thesaurus':
    url = 'http://www.m-w.com/cgi-bin/thesaurus'
    query = form_encode(va=key, book='Thesaurus')
if action == 'recipes':
    # url = 'http://www.epicurious.com/s97is.vts'
    # query = form_encode(action='filtersearch', filter='recipe-filter.hts',
    #                    collection='Recipes', queryType='and',
    #                    ResultTemplate='recipe-results.hts', keyword=key)
    url = 'http://www.epicurious.com/recipes/find/results'
    query = form_encode(search=key)
if action == 'yellow':
    # url = 'http://yp.yahoo.com/py/ypResults.py'
    # query = form_encode(stx=key, stp='a', tab='B2C',
    #                    city='Berkeley', state='CA', zip='94709', country='us',
    #                    slt='37.867199', sln='-122.259300', cs='5')
    url = 'http://www.google.com/local'
    query = form_encode(q=key, near='Berkeley, CA 94709')
if action == 'movies':
    # url = 'http://imdb.com/Find'
    # query = form_encode(select='All', For=key)
    url = 'http://imdb.com/find'
    query = form_encode(q=key, s='all')
if action == 'map':
    # url = 'http://maps.lycos.com/mapresults.asp'
    # query = [('AD2', q), ('AD3', city), ('AD4', 'USA')]
    # url = 'http://maps.yahoo.com/py/maps.py'
    # query = form_encode(Pyt='Tmap', addr=addr, csz=city, Country='us')
    url = 'http://maps.google.com/maps'
    query = form_encode(q=addr + ', ' + city)
if action == 'directions':
    # url = 'http://maps.lycos.com/directions.asp'
    # query = [('OAD2', '1730 La Loma Avenue'), ('OAD3', 'Berkeley, CA'),
    #          ('DAD2', q), ('DAD3', city)]
    # url = 'http://maps.yahoo.com/py/ddResults.py'
    # query = form_encode(Pyt='Tmap', newaddr='1730 La Loma Avenue',
    #                    newcsz='Berkeley, CA', newcountry='us',
    #                    newtaddr=addr, newtcsz=city, newtcountry='us')
    url = 'http://maps.google.com/maps'
    query = form_encode(q='1730 La Loma Avenue, Berkeley, CA to ' +
                          addr + ', ' + city)

# Post an event.

if form.object == 'event':
    if not form.title.strip():
        abort('Event: no title entered',
              'Please go back and enter a title for the event.')
    if not form.month.strip() or not form.day.strip():
        abort('Event: no date entered',
              'Please go back and choose a date for the event.')
    date = parse_date(form.month + '-' + form.day)
    if action == 'preview':
        query = form_encode(title=form.title, details=form.details,
                            month=form.month, day=form.day, preview=1)
        redirect('index.cgi?' + query)
    else: # action should be 'add'
        title = ' '.join(form.title.split())
        details = form.details.replace('\r\n', '\n').replace('\n\n', '\x01')
        details = ' '.join(details.split()).replace('\x01', '\t')
        append_records(join(WEB_ROOT, 'events.txt'), [(date, title, details)])

# Post a note (as a plain note or as a Kwiki kwestion).

if form.object == 'note':
    if not form.name.strip():
        abort('Note: no name entered',
              "Please go back and enter something in the box for your name.")
    if not form.note.strip():
        abort('Note: no text entered',
              'Please go back and enter some text for the note.')
    if action == 'preview':
        query = form_encode(name=form.name, note=form.note, preview=1)
        redirect('index.cgi?' + query)
    if action == 'post':
        name = ' '.join(form.name.split())
        note = form.note.replace('\r\n', '\n').replace('\n', '\x01')
        note = ' '.join(note.split()).replace('\x01', '\t')
        date = '%04d-%02d-%02d %02d:%02d' % local[:5]
        append_records(join(WEB_ROOT, 'notes.txt'), [(date, name, note)])
    if action == 'ask':
        question = ' '.join(form.note.split())
        name = ' '.join(form.name.split()) + ' asks'
        note = question + ' [answer@' + question + ']'
        line = '%04d-%02d-%02d %02d:%02d\t%s\t%s\n' % (
            local[:5] + (name, note))
        file = open(join(WEB_ROOT, 'notes.txt'), 'a')
        file.write(line)
        file.close()
    
# if action ==  'request':
#     if not form.name.strip():
#         abort('Request not added',
#               "Please go back and enter something in the box for your name.")
#     if not form.movie.strip():
#         abort('Request not added', "You didn't enter a movie.")
#     movie = form.movie.replace('\r\n', '\n').replace('\n', '\x01')
#     comment = form.comment.replace('\r\n', '\n').replace('\n', '\x01')
#     movie = ' '.join(movie.split()).replace('\x01', '\t')
#     comment = ' '.join(comment.split()).replace('\x01', '\t')
#     line = '%04d-%02d-%02d %02d:%02d\t%s\t%s\t%s\n' % (
#         local[:5] + (' '.join(form.name.split()), movie, comment))
#     if form.board == 'movierequests':
#         if form.id.strip(): id = '>' + form.id
#         else: id = '%.03f' % time.time()
#         file = open(join(WEB_ROOT, 'movierequests.txt'), 'a')
#         file.write('%s\t%s' % (id, line))
#         file.close()
#         url, query = 'movierequests.cgi', ''
#     else:
#         abort('Bug', "Huh? Wrong board. BUG!")    
#     pass

redirect(url + (query and '?' + query))
