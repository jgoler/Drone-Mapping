#!/bin/bash

# Usage: ./ns_pipeline.bash $kf_json

# get keyframe input folder, repo path, and output folder
kf_json=$1
source ./config.bash
echo -e "\n*** Repo path: ${repo}"
echo "*** Keyframe transform json: ${kf_json}"
out_path="${repo}/output"
train_folder=PROCESSED

# Get video name and percentage/algorithm from keyframe folder path
if [[ $kf_json =~ \/([^\/]+)\/([^\/]+)_transforms\.json$ ]]; then
    video_name="${BASH_REMATCH[1]}"
    downsample_name="${BASH_REMATCH[2]}"
    out_folder="${out_path}/${video_name}/${downsample_name}"
else
    echo "Error: Input json path must be in format: $/{video_name}/{downsample_name}_transforms.json"
    exit 1
fi

# create output json file
./retrieve_frames.py $kf_json

# copy output json to train folder. If file already exists, rename it with timestamp
train_json_path="${train_folder}/transforms.json"
if [ -f "$train_json_path" ]; then
    current_date_time=$(date "+%Y-%m-%d_%H-%M-%S")
    mv "$train_json_path" "${train_folder}/transforms_${current_date_time}.json"
fi
cp "$kf_json" "$train_json_path"

# run nerfstudio
CURRENT_DATE_TIME='$(date "+%Y-%m-%d_%H-%M-%S")'
ns-train nerfacto --data $train_folder --output_dir $out_folder --vis wandb --experiment_name "${downsample_name}_${video_name}"
ns-train splatfacto --data $train_folder --output_dir $out_folder --vis wandb --experiment_name "${downsample_name}_${video_name}"
