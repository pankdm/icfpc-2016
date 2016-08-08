#!/bin/bash

for i in $(seq 1 4000)
do
  fn=~/Dropbox\ \(Personal\)/icfpc2016/tasks/t${i}.txt
  if [ ! -e "$fn" ]; then continue; fi

  fn_sol=sols/s${i}_*
  have_sol=$(echo $fn_sol | perl -nle 'print m/\*$/ ? 0 : 1')
  if (( $have_sol > 0 )); then echo Skipping ${fn_sol}.; continue; fi;

  cat "$fn"  | python origami.py > sols/s${i}

  out=$(./submit.sh ${i} sols/s${i} 2> /dev/null)
  resemblance=$(echo $out | perl -ple 's/^.+resemblance\":([\d.]+).+$/$1/')

  echo $i $out $resemblance
  mv sols/s${i} sols/s${i}_${resemblance}

  sleep 3
done
