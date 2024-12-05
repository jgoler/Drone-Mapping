#!/bin/bash

# Function to find the latest config.yml file in a given directory
find_latest_config() {
    local search_dir=$1
    local latest_config=""

    # Find all config.yml files under /nerfacto and /splatfacto folders
    config_files=($(find "$search_dir" -regextype posix-extended -regex '.*\/config\.yml'))

    if [ ${#config_files[@]} -eq 0 ]; then
        echo "No config.yml files found in $search_dir"
        return
    fi

    # Sort the config files by their timestamp in the folder name and get the latest one
    latest_config=$(printf "%s\n" "${config_files[@]}" | sort -r | head -n 1)

    echo "$latest_config"
}

get_render_dir_from_search_dir() {
    local model_dir=$1
    local percentage=$(basename "$(dirname "$(dirname "$model_dir")")")
    local vid_name=$(basename "$(dirname "$model_dir")")
    local model_type=$(basename "$model_dir")
    local render_dir="$repo/$RENDERS/$vid_name/$percentage/$model_type"
    echo "$render_dir"
}

get_result_file_from_render_dir() {
    local render_dir=$1
    local vid_name=$(basename "$(dirname "$(dirname "$render_dir")")")
    local percentage=$(basename "$(dirname "$render_dir")")
    local model_type=$(basename "$render_dir")
    echo "$repo/$RESULTS/$vid_name/${percentage}_${model_type}.csv"
}

# Change to the directory of this script. Note that below command does not work if run using source command
cd "$(dirname "$0")"
echo -n "Current working directory: "
pwd

# Load configs and source the config file to import variables. Source find_latest_models.bash to use the function
./export_to_bash.py
source ./config.bash

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
echo "********** Splat ground truth **********"
echo "100p Splat model yml: $gt_splat_yml"
echo "100p Splat renders: $gt_splat_renders"
echo "Splat model already rendered. Skipping..."
echo "*******************************************"
# ns-render camera-path --load-config $gt_splat_yml --camera-path-filename $camera_path --output-path $gt_splat_renders --output-format images

# Render nerf / splat results
for model_dir in "${model_dirs[@]}"; do
    model_yml=$(find_latest_config "$model_dir")
    model_renders=$(get_render_dir_from_search_dir "$model_dir")
    render_dirs+=("$model_renders")
    # model_result_file=$(get_result_file "$model_dir")
    model_type=$(basename "$model_dir")
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
done

# Evaluate the renders
for render_dir in "${render_dirs[@]}"; do
    model_result_file=$(get_result_file_from_render_dir "$render_dir")
    echo "********** Evaluating model **********"
    # Create directory for model_result_file if it doesn't exist
    mkdir -p "$(dirname "$model_result_file")"
    if [ model_type == "nerfacto" ]; then
        ./eval_pipeline.py $render_dir $gt_nerf_renders $model_result_file
    else
        ./eval_pipeline.py $render_dir $gt_splat_renders $model_result_file
    fi
done