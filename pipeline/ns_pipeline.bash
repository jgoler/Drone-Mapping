#!/bin/bash

# Usage: ./ns_pipeline.bash $kf_folder

# get keyframe input folder, repo path, and output folder
kf_folder=$1
source ./config.bash
echo -e "\n*** Repo path: ${repo}"
echo "*** Keyframe folder: ${kf_folder}"
out_path="${repo}/output"

# Get video name and percentage/algorithm from keyframe folder path
if [[ $kf_folder =~ \/data\/keyframes\/([^\/]+)\/([^\/]+)$ ]]; then
    video_name="${BASH_REMATCH[1]}"
    percentage="${BASH_REMATCH[2]}"
    train_folder="${repo}/data/processed/${video_name}/${percentage}"
    out_folder="${out_path}/${video_name}/${percentage}"
    mkdir -p $train_folder
elif [[ $kf_folder =~ \/data\/frames\/([^\/]+)$ ]]; then
    video_name="${BASH_REMATCH[1]}"
    percentage="100p"
    train_folder="${repo}/data/processed/${video_name}/${percentage}"
    out_folder="${out_path}/${video_name}/${percentage}"
    mkdir -p $train_folder
else
    echo "Error: Input directory must be in format: $\{repo_path\}/data/(keyframes|frames)/video_name/percentage"
    exit 1
fi

# process to get camera poses with colmap
ns-process-data images --data $kf_folder --output_dir $train_folder

# run nerfstudio
CURRENT_DATE_TIME='$(date "+%Y-%m-%d_%H-%M-%S")'
ns-train nerfacto --data $train_folder --output_dir $out_folder --vis wandb --experiment_name ${video_name}
ns-train splatfacto --data $train_folder --output_dir $out_folder --vis wandb --experiment_name ${video_name}
