#!/bin/bash

# Change to the directory of this script. Subsequent scripts run relative to this directory. This does not work with source command
cd "$(dirname "$0")"

# Export config variables from yaml to bash
./export_to_bash.py

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

# # render ground truth images
# ./ns_render_gt.bash


