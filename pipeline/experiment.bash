#!/bin/bash

# Change to the directory of this script. Subsequent scripts run relative to this directory. This does not work with source command
cd "$(dirname "$0")"

# Export config variables from yaml to bash
./export_to_bash.py

# Collect keyframes using python script
# ./experiment_pipeline.py

# load config variables and construct folder paths
source ./config.bash

# Define the skip flags
skip_train=${1:-0}
skip_render=${2:-0}
skip_eval=${3:-0}

# run nerfstudio on each keyframe folder
for exp_name in "${experiments[@]}"; do
    ./model_pipeline.bash $exp_name $skip_train $skip_render $skip_eval & 
    pid=$!
    printf "\n------------------------------------------------\n\n"
    echo "Started pipeline for experiment ${exp_name}. Process ID: ${pid}"
    # wait for the training to finish before starting the next one
    wait $pid
done
