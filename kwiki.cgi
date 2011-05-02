#!/usr/bin/env python

from utils import *
from fastcgi import *
import os, time, re

MAX_WORDS = 8 # for excerpts in automatic edit summaries

def describe_date(date):
    sec = time.time() - date
    if sec >= 240*3600:
        y, l, d = time.localtime(date)[:3]
        return '%d %s %d' % (d, monthnames[l][:3], y)
        return '%d d ago' % int(round(sec/24./3600.))
    if sec >= 36*3600:
        return '%.1f d ago' % float(sec/24./3600.)
    if sec >= 10*3600:
        return '%d h ago' % int(round(sec/3600.))
    if sec >= 5400:
        return '%.1f h ago' % float(sec/3600.)
    if sec >= 600:
        return '%d m ago' % int(round(sec/60.))
    if sec >= 90:
        return '%.1f m ago' % float(sec/60.)
    return '%d s ago' % sec

def format_date(date):
    y, l, d, h, m, s = time.localtime(date)[:6]
    return '%s %d, %02d:%02d' % (monthnames[l][:3], d, h, m)
    return '%04d-%02d-%02d %02d:%02d:%02d' % (y, l, d, h, m, s)

def clean_line(text):
    return re.sub(r'\s+', ' ', text.strip())

def clean_tags(tags):
    taglist = re.split(',+', re.sub('[^a-z0-9,]', '', tags.lower()))
    taglist = sorted(set(taglist))
    return ' '.join(taglist).strip()

def describe_meta_changes(old_meta, new_meta):
    desc = []
    if old_meta['title'] != new_meta['title']:
        desc += ['Change title to <span class=title>%s</span>.' %
                 esc(new_meta['title'])]
    if old_meta['tags'] != new_meta['tags']:
        old_tags = set(old_meta['tags'].split())
        new_tags = set(new_meta['tags'].split())
        added_tags = new_tags - old_tags
        removed_tags = old_tags - new_tags
        def list_tags(tags):
            return ', '.join(['<span class=tag>%s</span>' % t for t in tags])
        if removed_tags:
            desc += ['Remove tag%s: %s.' %
                     (plural(removed_tags), list_tags(removed_tags))]
        if added_tags:
            desc += ['Add tag%s: %s.' %
                     (plural(added_tags), list_tags(added_tags))]
    return desc

def describe_body_changes(old_body, new_body):
    desc = []

    def phrase_list(phrases, max_words=MAX_WORDS):
        parts = []
        words = 0
        for phrase in phrases:
            chunk = phrase[:max_words - words]
            words += len(chunk)
            if chunk:
                parts += ['<span class="edit">%s</span>' % esc(' '.join(chunk))]
            if words == max_words:
                break
        return ' | '.join(parts)

    import difflib
    removed = [[]]
    added = [[]]
    for diff in difflib.ndiff(old_body.split(), new_body.split()):
        if diff.startswith('-'):
            removed[-1].append(diff[2:])
        elif removed[-1]:
            removed.append([])
        if diff.startswith('+'):
            added[-1].append(diff[2:])
        elif added[-1]:
            added.append([])
    if sum(removed, []):
        count = len(sum(removed, []))
        desc += ['<span class="remove-count">-%d</span> word%s (%s%s).' %
                 (count, plural(count), phrase_list(removed),
                  count > MAX_WORDS and '...' or '')]
    if sum(added, []):
        count = len(sum(added, []))
        desc += ['<span class="add-count">+%d</span> word%s (%s%s).' %
                 (count, plural(count), phrase_list(added),
                  count > MAX_WORDS and '...' or '')]
    return desc

def make_tag_menus(wiki, id, meta):
    ids = wiki.list_ids()
    tags, arrows, menus = [], [], []
    for tag in meta['tags'].split():
        if tags:
            tags += td(',', nbsp)
            arrows += td()
            menus += td()

        links = [li(link(other_id, wiki.get_title(other_id)))
                 for other_id in ids
                 if tag in wiki.get_tags(other_id) and other_id != id]
        arrow = '&#9660;'
        if links:
            menu = ['%d other page%s tagged ' % (len(links), plural(links)),
                    span(tag, c='tags'), ':', ul(links)]
        else:
            arrow = span(arrow, c='empty')
            empty = ' empty'
            menu = ['no other pages tagged ', span(tag, c='tags')]

        tags += td(tag, id='tag-' + tag, onmouseover="hover_menu('%s')" % tag)
        arrows += td(arrow, id='arrow-' + tag, c='arrow',
                     onmouseover="hover_menu('%s')" % tag,
                     onclick="event.stopPropagation(); show_menu('%s')" % tag)
        menus += td(div(menu, c='tag-menu', id='menu-%s' % tag))
    return table(tr(tags), tr(arrows), tr(menus))

def make_tag_list(wiki):
    counts = {}
    for id, title, tags, date, versions, old_ids in wiki.list_ittdvos():
        if 'retired' in tags:
            counts['retired'] = counts.get('retired', 0) + 1
        else:
            for tag in tags:
                counts[tag] = counts.get(tag, 0) + 1
    popular = [tr(th('Popular tags'))]
    once = []
    for tag in sorted(counts.keys()):
        count = counts[tag]
        url = request + '?' + form_encode(key=tag)
        onclick = "return add_tag('%s')" % tag
        if tag in ['retired', 'hidden']:
            onclick = "$('%s').checked = true; " % tag + onclick
        entry = link(url, tag, c='tag', onclick=onclick)
        if count > 1:
            popular += tr(td(entry, ' ', count), c=count_class(count))
        elif count == 1:
            once += [entry, ' ']
    return [table(popular, c='popular'),
            table(tr(th('Tags used only once')), tr(td(once)), c='once')]

def count_class(count):
    return 'c%d' % min(count, 29)

def age_class(date):
    age = time.time() - date
    if age < 3600:
        return 'hour-old'
    if age < 24*3600:
        return 'day-old'
    return ''

wiki = Wiki('kwiki-data')

path_info = os.environ.get('PATH_INFO', '')
if path_info.endswith('/'):
    redirect((request + path_info).rstrip('/'))
loc = os.environ.get('PATH_INFO', '').replace('/', '').strip()
title, action = (loc.split(':') + [''])[:2]
title, version = (title.split('.') + [0])[:2]
id, version = wiki.get_id(title), int(version)

if form.action.strip():
    action = form.action.split()[0]

if action == 'go':
    redirect(request + '/' + form.page)

if action == 'create':
    redirect(request + '/:new?' + form_encode(title=form.key))

if action == 'search':
    prologue('Kingman Hall: Search', 'style.css')
    keys = set(form.key.lower().split())
    records = wiki.list_ittdvos()
    records.sort(key=lambda (id, title, tags, date, versions, old_ids): -date)
    rows = [tr(th('Last edit', c='date'),
               th('Page', c='title'))]
    for id, title, tags, date, versions, old_ids in records:
        date, meta, body = wiki.get_page(id)
        excerpts = []
        body = body.lower()
        show, hit_tags = 1, {}
        for key in keys:
            if key in title.lower():
                continue
            for tag in tags:
                if key in tag:
                    hit_tags[tag] = 1
                    break
            else:
                pos = body.find(key)
                if pos < 0:
                    show = 0
                    break
                end = pos + len(key)
                before = body[pos - 20:pos].split(' ', 1)[-1]
                after = body[end:end + 20].rsplit(' ', 1)[0]
                excerpts += [' ', span('...', esc(before),
                                       span(body[pos:end], c='match'),
                                       esc(after), '...', c='excerpt')]
        if show:
            shown_tags = ''
            if hit_tags:
                shown_tags = span('(', ', '.join(sorted(hit_tags.keys())),
                                  ')', c='tags')
            rows.append(tr(td(format_date(date), c='date'),
                           td(link(request + '/' + id, title), ' ',
                                   span('v%d' % versions, c='versions'), ' ',
                                   shown_tags, excerpts, c='title')))
    write_template('kwiki-search.html',
                   pages=table(rows, c='pages'),
                   key=esc(form.key))
    epilogue()

if not title + action:
    prologue('Kingman Hall: Kwiki', 'style.css')
    rows = [tr(th('Last edit', c='date'),
               th('Page', c='title'))]
    records = wiki.list_ittdvos()
    records.sort(key=lambda (id, title, tags, date, versions, old_ids): -date)
    for id, title, tags, date, versions, old_ids in records:
        c = 'title'
        if 'hidden' in tags:
            c += ' hidden-page'
        if 'retired' in tags:
            c += ' retired-page'
        rows.append(tr(td(format_date(date), c='date'),
                       td(link(request + '/' + id, title, ' ',
                          span('v%d' % versions, c='versions')), ' ',
                          span(c='tags'), c=c),
                       id='page-' + id, c=age_class(date)))
    items = []
    for id in wiki.list_ids():
        quoted_tags = ["'%s'" % tag for tag in wiki.get_tags(id)]
        items.append("'%s': [%s]" % (id, ', '.join(quoted_tags)))
    write_template('kwiki-index.html',
                   pages=table(rows, id='pages', c='pages'),
                   page_tags=',\n    '.join(items),
                   tag_list=make_tag_list(wiki),
                   key=form.key)
    epilogue()

if action == 'new':
    prologue('Kingman Hall: Create a new page', 'style.css')
    write_template('kwiki-new.html', title=esc(form.title),
                   tags=esc(form.tags), body=esc(form.body))
    epilogue()

tags = []
meta, body, date = {'title': '', 'tags': ''}, '', time.time()
if wiki.contains(id):
    if title != id:
        redirect(request + '/' + id + (action and ':' + action or ''))
    title, tags, date, num_versions, old_ids = wiki.get_ttdvo(id)
    version = version or num_versions
    if version > num_versions:
        redirect(request + '/' + id + ':history')
    date, meta, body = wiki.get_page(id, version - 1)
elif action != 'save':
    # The page doesn't exist.
    if form.title:
        title = form.title
    url = request + '/:new?' + form_encode(title=title)
    new_ids = wiki.find_new_ids(id)
    if new_ids:
        prologue('Kingman Hall: Missing page', 'style.css')
        write(h1('Missing page'), p, 'There used to be a page entitled ',
              ldq, title, rdq, ', but it has moved to: ')
        write(ul([li(link(new_id, wiki.get_title(new_id)))
                  for new_id in new_ids]))
        write(p, 'Or, you can ', link(url, 'create a new page'),
              ' entitled ', ldq, title, rdq, '.')
        epilogue()
    else:
        redirect(url)

# By default, pages are visible to anyone and editable by anyone.
# Pages tagged 'protected' are visible to anyone, editable only in Kingman.
# Pages tagged 'private' are visible only in Kingman, editable only in Kingman.
access = ''

if 'protected' in tags:
    access = div(
        'This page is visible to anyone, ',
        'but can only be edited inside Kingman because it is tagged ',
        span('protected', c='tags'), '.', c='access')

if 'private' in tags:
    access = div(
        'This page is visible only inside Kingman because it is tagged ',
        span('private', c='tags'), '.', c='access')
    if not client.startswith('10.0.'):
        prologue('Kingman Hall: ' + meta['title'], 'style.css')
        write_template('kwiki-private.html', title=esc(meta['title']))
        epilogue()

if 'protected' in tags and action in ['edit', 'save']:
    if not client.startswith('10.0.'):
        prologue('Kingman Hall: ' + meta['title'], 'style.css')
        write_template('kwiki-protected.html', title=esc(meta['title']))
        epilogue()

if action == '':
    import utils
    utils.wiki = wiki
    utils.wikiurl = request
    prologue('Kingman Hall: ' + meta['title'], '../style.css')
    prev = []
    if version > 1:
        prev += [link('%s.%d' % (id, version - 1), 'v%d' % (version - 1)), dot]
    next = []
    if version < num_versions:
        next += [dot, link('./%s.%d:edit?note=Revert+to+version+%d.' %
                           (id, version, version), 'revert',
                           title='Edit version %d of this page.' % version)]
    if version < num_versions - 1:
        next += [dot, link('%s.%d' % (id, version + 1), 'v%d' % (version + 1))]
    if version < num_versions:
        next += [dot, 'current is ', link(id, 'v%d' % num_versions)]

    write_template('kwiki-view.html', title=esc(meta['title']),
                   tags=meta['tags'].replace(' ', ', '), access=access,
                   id=id, version=version, date=describe_date(date),
                   tagmenus=make_tag_menus(wiki, id, meta),
                   toc=format_toc(body), body=format_text(body),
                   prev=prev, next=next)
elif action == 'history':
    prologue('Kingman Hall: History of ' + ldq + meta['title'] + rdq,
             'style.css')
    rows = [tr(th('Version', c='version'),
               th('Date', c='datedesc'), #th('', c='date'),
               th('By', c='name'),
               th('Words', c='words'),
               th('Description of change', c='note'))]
    for version in reversed(range(num_versions)):
        date, meta, body = wiki.get_page(id, version)
        separator = ''
        if meta.get('note') and meta['note'].strip()[-1] not in '.!?':
            separator = '.'
        rows += tr(td(link('%s.%d' % (id, version + 1), div(version + 1)),
                      c='version'),
                   #td(describe_date(date), c='datedesc'),
                   td(format_date(date), c='date'),
                   td(esc(meta.get('name', '')), c='name'),
                   td(len(body.split()), c='words'),
                   td(esc(meta.get('note', '')), separator, ' ',
                      span(meta.get('delta', ''), c='delta'), c='note'),
                   c=age_class(date))
    write_template('kwiki-history.html', title=esc(title), tags=', '.join(tags),
                   id=id, version=version, date=describe_date(date),
                   history=table(rows, c='history'))
elif action == 'edit':
    prologue('Kingman Hall: Edit ' + ldq + title + rdq, 'style.css')
    revnote = ''
    if version < num_versions:
        revnote = [div(span('Note:', c='error'),
                   ' what you see below is an old version of this page. '
                   'Whatever you save will become the current version. '
                   'So, if you just save it without editing, the page '
                   'will revert to the way it was in version %d.' % version,
                   c='access')]
    write_template('kwiki-edit.html', title=esc(meta['title']),
                   tags=meta['tags'].replace(' ', ', '),
                   id=id, version=version, date=describe_date(date),
                   body=esc(body).strip(), revnote=revnote,
                   name=esc(form.name), note=esc(form.note))
elif action == 'save':
    old_meta = meta.copy()
    old_body = body
    if 'note' in meta:
        del meta['note']
    if 'name' in meta:
        del meta['name']
    if wiki.get_id(clean_line(form.title)):
        meta['title'] = clean_line(form.title)
    if clean_tags(form.tags):
        meta['tags'] = clean_tags(form.tags)
    if clean_line(form.note):
        meta['note'] = clean_line(form.note)
    if clean_line(form.name):
        meta['name'] = clean_line(form.name)
    if form.body.strip():
        body = form.body
    if not meta.get('name', ''):
        abort('Kwiki: no name entered',
              'Please go back and enter something in the box for your name.')
    new_id = wiki.get_id(meta['title'])
    if not new_id:
        abort('Kwiki: no valid title entered',
              'The page title must have at least one letter or number. ',
              'Please go back and edit the title.')
    if not body.strip():
        abort('Kwiki: no content entered',
              'Please go back and enter something for the page contents.')
    if form.new and wiki.contains(new_id):
        abort('Kwiki: duplicate page title',
              'The page title you entered is already in use. ',
              'Please go back and edit the title.')
    if form.preview:
        verb = form.new and 'Create' or 'Edit'
        prologue('Kingman Hall: %s %s%s%s' %
                 (verb, ldq, esc(meta['title']), rdq), 'style.css')
        import utils
        utils.wiki = wiki
        utils.wikiurl = request
        write_template('kwiki-preview%s.html' % (form.new and '-new' or ''),
                       title=esc(meta['title']), verb=verb, new=form.new,
                       tags=meta['tags'].replace(' ', ', '),
                       id=id, version=version, date=describe_date(date),
                       body=esc(body).strip(), preview=format_text(body),
                       name=esc(meta['name']), note=esc(meta.get('note', '')))
        epilogue()
#   date = '%04d-%02d-%02d %02d:%02d' % time.localtime()[:5]
#   name = meta['name']
    if wiki.contains(id):
        meta['delta'] = ' '.join(describe_meta_changes(old_meta, meta) +
                                 describe_body_changes(old_body, body))
#       note = 'just edited the Kwiki page [' + meta['title'] + ']'
    else:
        words = body.split()
        tags = ''
        if meta['tags']:
            tags = ' with tag%s: <span class="tag">%s</span>' % (
                plural(meta['tags'].split()), meta['tags'].replace(' ', ', '))
        meta['delta'] = ('Create page <span class="title">%s</span> ' +
                         '(<span class="edit">%s</span>%s)%s.') % (
                         esc(meta['title']), esc(' '.join(words[:MAX_WORDS])),
                         len(words) > MAX_WORDS and '...' or '', tags)
#       note = 'just created the Kwiki page [' + meta['title'] + ']'
    wiki.put_page(id, meta, body, merge=not form.new)
#   append_records(join(WEB_ROOT, 'notes.txt'), [(date, name, note)])
    redirect(request + '/' + new_id)
else:
    prologue('Kingman Hall: ' + meta['title'], 'style.css')
    write('Invalid action: "%s".' % esc(action))

epilogue()
