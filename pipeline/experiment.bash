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

# Render and Evaluate
./render_eval_script.bash
