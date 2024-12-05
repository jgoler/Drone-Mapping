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