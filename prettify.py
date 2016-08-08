import sys
import json


f = open(sys.argv[1], 'r')
data = f.read()

js = json.loads(data)
