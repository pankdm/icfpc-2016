import requests
from ratelimit import *
import json
import os.path
import os
import time

ERROR_LIMIT = 20

class Api:
    def __init__(self):
        self.base_url = 'http://2016sv.icfpcontest.org/api/'
        self.headers = {'X-API-Key': '137-e50485f99b1df06397414b5cd9f4f55d'}
        self.num_errors = 0

    def make_request_debug(self, endpoint):
        url = self.base_url + endpoint
        time.sleep(2)
        r = requests.get(url, headers=self.headers, data=data)
        print r
        return r


    # @rate_limited(2)
    def make_request(self, endpoint, data=None, use_json=True):
        time.sleep(2)
        url = self.base_url + endpoint
        r = requests.get(url, headers=self.headers, data=data)
        if not r.ok:
            print r
            raise Exception(r.text)
        if use_json:
            return json.loads(r.text)
        else:
            return r.text

    def hello_world(self):
        self.make_request('hello')

    def snapshot_list(self):
        return self.make_request('snapshot/list')

    def lookup_blob(self, hash, use_json=True):
        return self.make_request('blob/{}'.format(hash), use_json=use_json)

    def get_new_problems(self):
        all_snapshots = self.snapshot_list()
        # print all_snapshots

        time = 0
        hash = None
        for info in all_snapshots['snapshots']:
            cur_time = info['snapshot_time']
            cur_hash = info['snapshot_hash']
            if cur_time > time:
                hash = cur_hash
                time = cur_time

        print 'Found latest hash: {} for timestamp {}'.format(
            hash,
            cur_time
        )
        blob = self.lookup_blob(hash)

        snapshot_name = 'snapshots/{}'.format(time)
        if not os.path.isfile(snapshot_name):
            print 'Saving snapshot to {}'.format(snapshot_name)
            self.write_to_file(
                data=json.dumps(blob, indent=2),
                file_name=snapshot_name)
            os.unlink('latest_snapshot')
            os.symlink(snapshot_name, 'latest_snapshot')

        problems = blob['problems']
        print 'Found {} problems'.format(len(problems))

        num_downloaded = 0
        for p in problems:
            p_id = p['problem_id']
            p_hash = p['problem_spec_hash']

            file_name = 'tasks/t{}.txt'.format(p_id)
            if not os.path.isfile(file_name):
                print '"{}" doesnt exists --> downloading...'.format(
                    file_name
                )
                try:
                    p_blob = self.lookup_blob(p_hash, use_json=False)
                    self.write_to_file(data=p_blob, file_name=file_name)
                    num_downloaded += 1
                except:
                    self.num_errors += 1
                    print 'Errors: ', self.num_errors
                    if self.num_errors > ERROR_LIMIT:
                        raise Exception(r.text)


        print 'Downloaded {} files'.format(num_downloaded)

    def write_to_file(self, data, file_name):
        f = open(file_name, 'wt')
        f.write(data)
        f.close()


if __name__ == "__main__":
    api = Api()
    # api.hello_world()
    api.get_new_problems()
