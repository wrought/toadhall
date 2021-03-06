#!/usr/bin/python

from utils import *
from fastcgi import *

music = '&#x266b;'

# Read the current data about computers detected by the netscan script.

records = []
for fields in read_records('/tmp/netscan.txt', 5, ' '):
    ip_address, ethernet_address, name, netbios, itunes_library = fields[:5]
    shares = sorted(fields[5:], key=lambda f: f.lower())
    windows_path = macosx_path = ''
    if int(netbios):
        windows_path = '\\\\' + ip_address
        macosx_path = 'smb://' + ip_address
    records.append((name, ip_address, ethernet_address,
                    windows_path, macosx_path, itunes_library, shares))
if form.sort == 'address':
    records.sort(key=lambda r: r[1] and map(int, r[1].split('.')))
else:
    records.sort(key=lambda r: r[0].lower())

# Format the rows of the listing.

windows_help = ['Click Start, then', br, 'Run..., then type:']
macosx_help = ['In the Finder,', br, 'press &#x2318;K and type:']
rows = tr(th(link('netscan.cgi?sort=name', 'Computer Name', c='plain')),
          th(link('netscan.cgi?sort=address', 'Address', c='plain')),
          th('Shared Folders', br, music, ' iTunes Music'),
          th('Windows', div(windows_help, c='note')),
          th('Mac OS X', div(macosx_help, c='note')))
parity = ''
for (name, ip_address, ethernet_address,
     windows_path, macosx_path, itunes_library, shares) in records:
    parity = (parity == 'odd') and 'even' or 'odd'
    if itunes_library:
        shares.insert(0, music + ' ' + itunes_library)
    rows += tr(td(name, c='hostname', title=ethernet_address),
               td(ip_address or 'none'),
               td(br.join(shares), c='shares'),
               td(windows_path),
               td(macosx_path),
               c=parity)

# Write out the network scan listing page.

prologue('Kingman Hall: Network Scan', 'style.css')
write_template('netscan.html',
               listing=table(rows, pad=1, space=0, c='netscan'))
epilogue()
