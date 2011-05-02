#!/usr/bin/env python

import math
def taper(x):
    pi = 3.14159265358979
    return math.atan(x)/(pi/2)

def hex_color((red, green, blue)):
    return '#%02x%02x%02x' % (red*255.999, green*255.999, blue*255.999)

def interpolate((r, g, b), (nr, ng, nb), t):
    return (r*(1.-t) + nr*t, g*(1.-t) + ng*t, b*(1.-t) + nb*t)

red = (0xaa/255.999, 0, 0)
white = (1, 1, 1)
black = (0, 0, 0)

rules = []
for count in range(2, 30):
    x = count/4.
    rules.append('.wiki .tag-list tr.c%d { color: %s; } ' %
                 (count, hex_color(interpolate(white, black, taper(x)))))
    rules.append('.wiki .tag-list tr.c%d a.tag { color: %s; } ' %
                 (count, hex_color(interpolate(white, red, taper(x)))))
#   rules.append('.wiki .tag-list tr.c%d a.tag:hover { color: %s; } ' %
#                (count, hex_color(interpolate(white, red, taper(x*2)))))

for count in range(20, 30):
    rules.append('.wiki .tag-list tr.c%d { font-weight: bold; }' % count)

for rule in rules:
    print rule
