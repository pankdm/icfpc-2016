#!/bin/bash

k=$1
mod=$2
if [ -z $k ]; then k=0; mod=1; fi

#for i in $(seq 6 30)
for i in $(cat new_queue.txt | cut -d' ' -f1)
do
  if (( $(( $i % $mod )) != $k )); then continue; fi

  fn=~/Dropbox\ \(Personal\)/icfpc2016/tasks/t${i}.txt
  if [ ! -e "$fn" ]; then continue; fi

  fn_full_sol="sols/s${i}_1.0"
  if [ -e "$fn_full_sol" ]; then echo "Skipping $i (already 1.0)"; continue; fi


  fn_sol=sols/rot_candidates/s${i}_rot0
  if [ -e "$fn_sol" ]; then
    echo "Skipping $i ($fn_sol) (previously computed)"
  else
    echo ". computing $i - 0"
    cat "$fn"  | ./origami_deploy_rot.py --rot_triplet='1 0 1' > "${fn_sol}_tmp"
    mv "${fn_sol}_tmp" "$fn_sol"
  fi



  # fn_sol=sols/rot_candidates/s${i}_rotX
  # if [ -e "$fn_sol" ]; then
  #   echo "Skipping $i ($fn_sol) (previously computed)"
  # else
  #   fn_rot=rotations/${i}
  #   if [ -e "$fn_rot" ]; then
  #     if [ "$(cat $fn_rot)" != "1 0 1" ]; then
  #       echo ". computing $i - X $(cat $fn_rot)"
  #       cat "$fn"  | ./origami_deploy_rot.py --rot_triplet="$(cat $fn_rot)" > "${fn_sol}_tmp"
  #       mv "${fn_sol}_tmp" "$fn_sol"
  #     fi
  #   fi
  # fi
  #
  #
  # fn_sol=sols/rot_candidates/s${i}_rotY
  # if [ -e "$fn_sol" ]; then
  #   echo "Skipping $i ($fn_sol) (previously computed)"
  # else
  #   fn_rot=rotations/${i}
  #   if [ -e "$fn_rot" ]; then
  #     if [ "$(cat $fn_rot)" != "1 0 1" ]; then
  #       echo ". computing $i - Y $(cat $fn_rot)"
  #       cat "$fn"  | ./origami_deploy_rot.py --rot_triplet="$(cat $fn_rot)" > "${fn_sol}_tmp"
  #       mv "${fn_sol}_tmp" "$fn_sol"
  #     fi
  #   fi
  # fi

done
