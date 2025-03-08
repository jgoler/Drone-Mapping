#!/bin/bash

# Change to the directory of this script. Note that below command does not work if run using source command
cd "$(dirname "$0")"
echo -n "Current working directory: "
pwd

# Load configs and source the config file to import variables. Source utils.bash to use the utility functions
./export_to_bash.py
source ./config.bash
source ./utils.bash

# wait for outstanding training processes to finish
echo "Waiting for training script to finish..."
wait $(<experiment_training_pid.txt)
echo "All outstanding training processes finished. Begin rendering and evaluation."

# render ground truth results. We'll skip this as the ground truth models are already rendered
gt_nerf_yml=$(find_latest_config "$gt_nerf_dir")
gt_nerf_renders=$(get_render_dir_from_search_dir "$gt_nerf_dir")
gt_splat_yml=$(find_latest_config "$gt_splat_dir")
gt_splat_renders=$(get_render_dir_from_search_dir "$gt_splat_dir")
echo "********** NeRF ground truth **********"
echo "100p NeRF model yml: $gt_nerf_yml"
echo "100p NeRF renders: $gt_nerf_renders"
echo "NeRF model already rendered. Skipping..."
echo "*******************************************"
# ns-render camera-path --load-config $gt_nerf_yml --camera-path-filename $camera_path --output-path $gt_nerf_renders --output-format images
echo ""
echo "********** Splat ground truth **********"
echo "100p Splat model yml: $gt_splat_yml"
echo "100p Splat renders: $gt_splat_renders"
echo "Splat model already rendered. Skipping..."
echo "*******************************************"
echo ""
# ns-render camera-path --load-config $gt_splat_yml --camera-path-filename $camera_path --output-path $gt_splat_renders --output-format images

# Render nerf / splat results
for model_dir in "${model_dirs[@]}"; do
    model_yml=$(find_latest_config "$model_dir")
    model_renders=$(get_render_dir_from_search_dir "$model_dir")
    render_dirs+=("$model_renders")
    model_result_file=$(get_result_file_from_render_dir "$model_dir")
    model_type=$(basename "$model_dir")
    echo ""
    echo "********** Rendering model **********"
    echo "model yml: $model_yml"
    echo "model renders: $model_renders"
    echo "model result file: $model_result_file"
    echo "*******************************************"
    # First, render the model
    ns-render camera-path --load-config $model_yml --camera-path-filename $camera_path --output-path $model_renders --output-format images &
    pid=$!
    echo "Started NS render for ${model_renders}. Process ID: ${pid}"
    wait $pid
    echo "Finished rendering ${model_renders}"
done

skip=1  # Skip evaluation for existing renders for now
# Evaluate the renders in directories listed in config.yml render_dirs
if [ $skip -eq 0 ]; then
    ./ns_eval_pipeline.bash
fi
