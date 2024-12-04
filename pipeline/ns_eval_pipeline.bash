#!/bin/bash

cd "$(dirname "$0")"
source ./config.bash

model_yml="/home/navlab/NeRF/nerfstudio/outputs/JackLakeLag/CombinedVideo/Nerfacto100Percent/nerfacto/2024-08-27_014642/config.yml"
model_renders="${repo}/renders/JackLakeLag/ground_truth"
camera_path="/home/navlab/NeRF/nerfstudio/data/JackLakeLag/CombinedVideo/Presentation-Render-2024-08-27_14-49.json"

mkdir -p $model_renders
ns-render camera-path --load-config $gt_model_yml --camera-path-filename $camera_path --output-path $gt_renders --output-format images


