#!/bin/bash

# Change to the directory of this script. Note that below command does not work if run using source command
cd "$(dirname "$0")"
echo -n "Current working directory: "
pwd
# Source the config file to import variables
source ./config.bash

gt_model_yml="/home/navlab/NeRF/nerfstudio/outputs/JackLakeLag/CombinedVideo/Nerfacto100Percent/nerfacto/2024-08-27_014642/config.yml"
gt_renders="${repo}/renders/JackLakeLag/ground_truth"
camera_path="/home/navlab/NeRF/nerfstudio/data/JackLakeLag/CombinedVideo/Presentation-Render-2024-08-27_14-49.json"

cd /home/navlab/NeRF/nerfstudio  # We need to be in this directory for the render to work
mkdir -p $gt_renders
ns-render camera-path --load-config $gt_model_yml --camera-path-filename $camera_path --output-path $gt_renders --output-format images
