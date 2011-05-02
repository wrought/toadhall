#!/usr/bin/python -S

from utils import *
from fastcgi import form

write_file('announcement.txt', form.announcement)
redirect('.')
