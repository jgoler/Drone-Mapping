#!/bin/bash

# Collect keyframes using python script
./experiment_pipeline.py

# collect keyframe folder paths in an array
mapfile -t kf_folders_array < ./kf_folders.txt

# run nerfstudio on each keyframe folder
for kf_folder in "${kf_folders_array[@]}"; do
    ./ns_pipeline.bash $kf_folder & 
    pid=$!
    echo "Started NS pipeline for ${kf_folder}. Process ID: ${pid}"
    # wait for the training to finish before starting the next one
    wait $pid
done