#!/bin/bash

echo Content-Type: text/plain
echo
export PATH=$PATH:/sbin:/usr/sbin
sudo /etc/init.d/netatalk restart 2>&1
echo
/usr/bin/nbplkup
