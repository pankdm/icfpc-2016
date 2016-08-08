#!/bin/bash

for f in `ls -1 tasks/*`; do
  png=$(echo $f | sed 's|tasks/||' | sed 's|txt|png|')
  if [ -e "img/${png}" ]; then continue; fi
  echo $f, $png
  cat $f | python visualize/convert_to_png.py  "img/${png}"
done
