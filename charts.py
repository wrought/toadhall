from colour import *

encoding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

def encode(points, limit):
    data = ''
    limit = float(limit)
    for point in points:
        if point is None:
            data += '_'
        else:
            value = max(0, min(1, point/limit))
            data += encoding[int(value*(len(encoding) - 0.001))]
    return 's:' + data

def params(**kwargs):
    return '&'.join('%s=%s' % pair for pair in kwargs.items())

def sparkline(width, height, data, limit, line_colour, line_width=1, stops=[]):
    fill_colour = line_colour.blend(white)
    markers = ['B,%s,0,0,0' % hex(fill_colour)]
    for stop in stops:
        markers.append('v,ffffff,0,%g,1' % stop)
    return 'http://chart.apis.google.com/chart?' + params(
        cht='ls', chs='%dx%d' % (width, height), chd=encode(data, limit),
        chco=hex(line_colour), chm='|'.join(markers),
        chls='%g,1,0' % line_width, chf='bg,s,ffffff00')

def sparkbar(width, height, data, limit, line_colour, line_width=1, stops=[]):
    fill_colour = line_colour.blend(white)
    markers = ['v,ffffff,0,%g,1' % stop for stop in stops]
    bar_width = int((width - 1)/ len(data))
    return 'http://chart.apis.google.com/chart?' + params(
        cht='bvs', chs='%dx%d' % (width, height), chbh='%d,0,0' % bar_width,
        chd=encode(data, limit), # + ',' + 'D'*len(data),
        chco='%s,%s' % (hex(fill_colour), hex(line_colour)),
        chm='|'.join(markers), chf='bg,s,ffffff00')

# Year labels
# chxs='0,666666,7,0',
# chxt='x', chxl='0:|2006|2007|2008|', chxp='0,3,12,21', chxr='0,0,24')
