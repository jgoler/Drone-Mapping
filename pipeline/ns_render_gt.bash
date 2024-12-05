#!/bin/bash

# Change to the directory of this script. Note that below command does not work if run using source command
cd "$(dirname "$0")"
echo -n "Current working directory: "
pwd

# Load configs and source the config file to import variables
./export_to_bash.py
source ./config.bash

# wait for outstanding training processes to finish
echo "Waiting for training script to finish..."
wait $(<experiment_training_pid.txt)
echo "All outstanding training processes finished. Begin rendering and evaluation."

gt_model_search_dir="/home/navlab/NeRF/nerfstudio/outputs/JackLakeLag/CombinedVideo/Nerfacto100Percent/"
gt_renders="${repo}/renders/JackLakeLag/100p"
camera_path="/home/navlab/NeRF/nerfstudio/data/JackLakeLag/CombinedVideo/Presentation-Render-2024-08-27_14-49.json"
yml_files=($(find /home/navlab/NeRF/nerfstudio/outputs/JackLakeLag/CombinedVideo -regex ".*/nerfacto/.*" -name "config.yml"))
gt_model_yml=${yml_files[0]}

echo "Ground truth model yml: ${gt_model_yml}"

# cd /home/navlab/NeRF/nerfstudio  # We need to be in this directory for the render to work
mkdir -p $gt_renders
ns-render camera-path --load-config $gt_model_yml --camera-path-filename $camera_path --output-path $gt_renders --output-format images

# render nerf results and evaluate
declare -a model_ymls
declare -a model_search_dirs
# mapfile -t out_folders_array < ./out_folders.txt
for out_folder in "${out_folders_array[@]}"; do
    ./ns_eval_pipeline.bash $out_folder &
    pid=$!
    echo "Started NS render efor ${out_folder}. Process ID: ${pid}"
    # wait for the rendering to finish before starting the next one
    wait $pid
done