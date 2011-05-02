#!/usr/bin/python

from utils import *
from fastcgi import form, request
import sys, time, os, re, cgitb; cgitb.enable()

BACKUP_DIR = '/root/backups'

if form.archive:
    archive_path = os.path.join(BACKUP_DIR, form.archive)
    assert archive_path.endswith('.tar.gz')
    if not os.path.exists(archive_path):
        print 'Content-Type: text/html; charset=iso-8859-1'
        print
        print 'Archive %s does not exist.' % form.archive
        sys.exit()

if form.archive and form.filename:
    # Retrieve a selected file from a backup archive.

    basename = form.filename.split('/')[-1]
    print 'Content-Type: application/octet-stream; name="%s"' % basename
    print 'Content-Disposition: attachment; filename="%s"' % basename
    print
    safe_name = form.filename.replace("'", "'\\''")
    if not safe_name.startswith('./'):
        safe_name = './' + safe_name
    pipe = os.popen("tar xOfz '%s' '%s'" % (archive_path, safe_name))
    while 1:
        data = pipe.read(65536)
        if not data: break
        write(data)
    sys.exit()

prologue('Kingman Hall: Automatic Backups', 'style.css')

if form.archive:
    # Parse the output of tar to get the list of files in the selected archive.

    records = []
    for line in os.popen("tar tvfz %s" % archive_path).readlines():
# 0         1         2         3         4         5
# 0123456789012345678901234567890123456789012345678901
# -rw-r--r-- 0/0           19968 2002-08-13 22:43:12 ./
        modes = line[:10]
        size = int(line[15:30].strip())
        date = line[31:50].strip().replace(' ', '&nbsp;')
        file = line[51:].strip()
        if file.startswith('./'): file = file[2:]
        if not modes.startswith('d'):
            records.append((file, date, size))

    # Sort the listing according to the selected sort key.

    sortkey = form.sortkey or 'filename'
    if sortkey == 'date':
        compare = lambda (fa, da, sa), (fb, db, sb): cmp(da, db)
    elif sortkey == 'size':
        compare = lambda (fa, da, sa), (fb, db, sb): cmp(sa, sb)
    else:
        compare = cmp
    if form.reverse:
        oldcompare = compare
        compare = lambda a, b: oldcompare(b, a)
    records.sort(compare)

    # Produce the listing of the contents of the archive.

    rows = []
    for file, date, size in records:
        fields = form_encode(archive=form.archive, filename=file)
        rows += tr(td(date, c='date'), td(str(size), c='size'),
                   td(link('backup.cgi?' + fields, file), c='filename'))
    write_template('backup-contents.html', listing=rows, archive=form.archive)

else:
    # List all available backup archives.

    listings = {}
    for category in ['incremental', 'daily', 'weekly', 'monthly']:
        listing = []
        filenames = os.listdir(os.path.join(BACKUP_DIR, category))
        filenames.sort()
        for filename in filenames:
            if filename.endswith('.tar.gz'):
                archive = os.path.join(category, filename)
                path = os.path.join(BACKUP_DIR, archive)
                mtime = os.path.getmtime(path)
                size = os.path.getsize(path)
                y, l, d, h, m, s = time.localtime(mtime)[:6]
                date = '%04d-%02d-%02d at %02d:%02d:%02d' % (y, l, d, h, m, s)
                listing += [link(form_url('backup.cgi', archive=archive),
                                 'archive created on ' + date),
                            ' (%d bytes)' % size, br]
        listings[category] = listing
    write_template('backup.html', **listings)

epilogue()
