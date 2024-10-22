#!/bin/bash

# Collect keyframes using python script
./experiment_pipeline.py

# collect keyframe folder paths in an array
mapfile -t kf_folders_array < ./kf_folders.txt

# create array to keep track of process ids of nerfstudio runs
declare -a pid_array

# run nerfstudio on each keyframe folder
for kf_folder in "${kf_folders_array[@]}"; do
    ./ns_pipeline.bash $kf_folder & 
    pid_array+=($!)
    echo "Started NS pipeline for ${kf_folder}. Process ID: $!"
done

# wait for all processes to finish
for pid in "${pid_array[@]}"; do
    wait $pid
done