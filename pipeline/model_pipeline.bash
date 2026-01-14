#!/usr/bin/bash

# Source the config file and utility functions
source ./config.bash
source ./utils.bash

# Get input arguments
exp_name=$1  
skip_train=$2
skip_render=$3
skip_eval=$4

# Construct the folder paths from the config variables
train_dir="${proj_dir}/${processed}"
model_dir="${proj_dir}/${models}"
render_dir="${proj_dir}/${renders}/${exp_name}"
result_file="${proj_dir}/${results}/${exp_name}.csv"
comparison_dir="${proj_dir}/${results}/${exp_name}_comparisons"
abs_camera_path="${proj_dir}/${camera_path}"


# Check if all arguments are provided
if [ -z "$train_dir" ] || [ -z "$model_dir" ] || [ -z "$render_dir" ] || [ -z "$result_file" ]; then
    echo "Missing directory paths in config."
    echo "Check config.yaml for paths and make sure to export to bash and source ./config.bash."
    exit 1
elif [ -z "$full_transforms" ] || [ -z "$camera_path" ]; then
    echo "full_transforms or camera_path is not defined in config.bash"
    exit 1
elif [ -z "$exp_name" ]; then
    echo "Usage: ./model_pipeline.bash <exp_name>"
    echo "Missing argument: exp_name"
    exit 1
fi

if [ "$skip_train" -ne 0 ] || [ "$skip_render" -ne 0 ] || [ "$skip_eval" -ne 0 ]; then
    echo "Skip flags - skip_train: $skip_train, skip_render: $skip_render, skip_eval: $skip_eval"
fi

if [ "$skip_train" -eq 0 ] || [ "$skip_render" -eq 0 ]; then
    # Either training or rendering is not skipped
    # As of nerfstudio v1.1.4, transforms file must match the one used during training for rendering
    # Create transforms file by calling retrieve_frames.py. This script will create a transforms file in the train_dir
    # Script exits if retrieve_frames.py fails
    echo "Generating transforms file for experiment ${exp_name}..."
    ./retrieve_frames.py $exp_name
    if [ $? -ne 0 ]; then
        echo "retrieve_frames.py failed, exiting."
        exit 1
    fi
fi

# Train the model. Set skip_train=0 when running experiment.bash to enable training
if [ "$skip_train" -ne 0 ]; then
    echo "Skipping training as per the skip_train flag."
else
    if [[ "$exp_name" = *"nerf"* ]]; then
        echo "Experiment name contains 'nerf'. Assuming nerf experiment."
        ns-train nerfacto --data $train_dir --output_dir $model_dir --pipeline.datamanager.images-on-gpu True --vis wandb --experiment_name $exp_name --project_name drone_mapping
    elif [[ "$exp_name" = *"splat"* ]]; then
        echo "Experiment name contains 'splat'. Assuming splat experiment."
        ns-train splatfacto --data $train_dir --output_dir $model_dir --pipeline.datamanager.cache-images "gpu" --pipeline.datamanager.images-on-gpu True --vis wandb --experiment_name $exp_name --project_name drone_mapping
    else
        echo "Experiment name must contain 'splat' or 'nerf'"
        exit 1
    fi
fi

# Extract the model config and render the model
if [ "$skip_render" -ne 0 ]; then
    echo "Skipping rendering as per the skip_render flag."
else
    model_config=$(find_latest_config "${model_dir}/${exp_name}")
    dataparser=$(./find_dataparser.py "${model_dir}/${exp_name}")
    if [ $? -ne 0 ]; then
        echo "find_dataparser.py failed for experiment ${exp_name}. Run the script manually to debug."
        exit 1
    fi
    abs_camera_path="${proj_dir}/${camera_path}/${exp_name}_camera_path.json"
    ./camera_path.py $dataparser $abs_camera_path
    if [ $? -ne 0 ]; then
        echo "camera_path.py failed for experiment ${exp_name}. Run the script manually to debug."
        exit 1
    fi
    ns-render camera-path --load-config $model_config --camera-path-filename $abs_camera_path --output-path $render_dir --output-format images
fi

# Evaluate the model
if [ "$skip_eval" -ne 0 ]; then
    echo "Skipping evaluation as per the skip_eval flag."
else
    ./eval_pipeline.py $render_dir $result_file $exp_name --save_comparisons $comparison_dir
    if [ $? -ne 0 ]; then
        echo "eval_pipeline.py failed for experiment ${exp_name}. Run the script manually to debug."
        exit 1
    fi
    echo "Evaluation completed successfully for experiment ${exp_name}."
fi
