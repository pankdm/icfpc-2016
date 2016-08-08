#!/usr/bin/env python2

import os

for line in open("../approx2_queue.txt"):
    pid = int(line.split()[0])
    print("%d\n" % pid)
    fname1 = "output/%d.out" % pid
    fname2 = "exact/%d.out" % pid
    fname = fname1
    if os.path.isfile(fname2):
        fname = fname2
    os.system("../curl_api/submit.sh %d %s; sleep 10" % (pid, fname))
