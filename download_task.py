from api import *
import json
import sys

task_id = int(sys.argv[1])

f = open('latest_snapshot')
snapshot = json.loads(f.read())

api = Api()

for p in snapshot['problems']:
    p_id = p['problem_id']
    p_hash = p['problem_spec_hash']
    if p_id == task_id:
        file_name = 'tasks/t{}.txt'.format(p_id)
        if not os.path.isfile(file_name):
            print '"{}" doesnt exists --> downloading...'.format(
                file_name
            )
            p_blob = api.lookup_blob(p_hash, use_json=False)
            api.write_to_file(data=p_blob, file_name=file_name)
