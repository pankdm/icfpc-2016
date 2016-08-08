#!/usr/bin/env bash

flist=`find output -type f -print0 | xargs -0 stat -f "%m %N" | sort -rn | head -n 10000 | cut -f2- -d" "`
for f in $flist; do
    num=$(echo "$f" | egrep -o [0-9]+)
    if [ $num -gt 0 ]; then
        echo $num
        ../curl_api/submit.sh $num $f
        sleep 6
        echo
    fi
done
