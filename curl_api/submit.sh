curl --compressed -L -H Expect: -H 'X-API-Key: 137-e50485f99b1df06397414b5cd9f4f55d' \
  -F "problem_id=${1}" -F "solution_spec=@${2}" \
  'http://2016sv.icfpcontest.org/api/solution/submit'
