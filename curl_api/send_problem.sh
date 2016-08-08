% curl --compressed -L -H Expect: -H 'X-API-Key: 137-e50485f99b1df06397414b5cd9f4f55d' \
 -F 'solution_spec=@{2}' -F "publish_time=${1}" \
 'http://2016sv.icfpcontest.org/api/problem/submit'
