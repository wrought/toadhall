#!/usr/bin/python -S

from utils import *

announcement=read_file('announcement.txt')

prologue('Kingman Hall: Website Administration', '/style.css')
write_template('admin/admin.html', announcement=esc(announcement))
epilogue()
