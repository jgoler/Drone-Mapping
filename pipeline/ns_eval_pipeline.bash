#!/bin/bash

# Change to the directory of this script. Note that below command does not work if run using source command
cd "$(dirname "$0")"
echo -n "Current working directory: "
pwd

# Load configs and source the config file to import variables. Source utils.bash to use the utility functions
./export_to_bash.py
source ./config.bash
source ./utils.bash

# Get renders of ground truth models
gt_nerf_yml=$(find_latest_config "$gt_nerf_dir")
gt_nerf_renders=$(get_render_dir_from_search_dir "$gt_nerf_dir")
gt_splat_yml=$(find_latest_config "$gt_splat_dir")
gt_splat_renders=$(get_render_dir_from_search_dir "$gt_splat_dir")
echo "********** NeRF ground truth **********"
echo "100p NeRF model yml: $gt_nerf_yml"
echo "100p NeRF renders: $gt_nerf_renders"
echo "*******************************************"
echo "********** Splat ground truth **********"
echo "100p Splat model yml: $gt_splat_yml"
echo "100p Splat renders: $gt_splat_renders"
echo "*******************************************"

# Perform evaluations
for render_dir in "${render_dirs[@]}"; do
    model_result_file=$(get_result_file_from_render_dir "$render_dir")
    echo "********** Evaluating model **********"
    # # Create directory for model_result_file if it doesn't exist
    # mkdir -p "$(dirname "$model_result_file")"
    if [ model_type == "nerfacto" ]; then
        ./eval_pipeline.py $render_dir $gt_nerf_renders $model_result_file
    else
        ./eval_pipeline.py $render_dir $gt_splat_renders $model_result_file
    fi
done
