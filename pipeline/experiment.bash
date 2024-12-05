#!/bin/bash

# Change to the directory of this script. Subsequent scripts run relative to this directory. This does not work with source command
cd "$(dirname "$0")"

# store process id of current script
echo $$ > "experiment_training_pid.txt"

# Export config variables from yaml to bash
./export_to_bash.py

# Collect keyframes using python script
# ./experiment_pipeline.py

# load config variables with folder paths
source ./config.bash

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

# # render nerf results and evaluate
# declare -a out_folders_array
# mapfile -t out_folders_array < ./out_folders.txt
# for out_folder in "${out_folders_array[@]}"; do
#     ./ns_eval_pipeline.bash $out_folder &
#     pid=$!
#     echo "Started NS render for ${out_folder}. Process ID: ${pid}"
#     # wait for the rendering to finish before starting the next one
#     wait $pid
# done
