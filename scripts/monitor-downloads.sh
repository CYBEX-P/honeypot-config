#!/bin/sh

dir="/home/cowrie/cowrie/var/lib/cowrie/downloads/"
inotifywait -m -e create --format '%f' $dir | while read f
do
  /home/cybex-user/check-hash.py "$dir$f"
done
