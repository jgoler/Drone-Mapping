#!/usr/bin/bash

# Source the config file and utility functions
source ./config.bash
source ./utils.bash

# Get input argument
exp_name=$1
skip_train=${2:-0}

# Construct the folder paths from the config variables
train_dir="${proj_dir}/${processed}"
model_dir="${proj_dir}/${models}"
render_dir="${proj_dir}/${renders}/${exp_name}"
result_file="${proj_dir}/${results}/${exp_name}.csv"
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



# Train the model
if [ "$skip_train" -ne 0 ]; then
    echo "Skipping training as per the skip_train flag."
else
    # Create transforms file by calling retrieve_frames.py. This script will create a transforms file in the train_dir
    # Script exits if retrieve_frames.py fails
    ./retrieve_frames.py $exp_name
    if [ $? -ne 0 ]; then
        echo "retrieve_frames.py failed, exiting."
        exit 1
    fi
    if [[ "$exp_name" = *"nerf"* ]]; then
        echo "Experiment name contains 'nerf'. Assuming nerf experiment."
        ns-train nerfacto --data $train_dir --output_dir $model_dir --vis wandb --experiment_name $exp_name
    elif [[ "$exp_name" = *"splat"* ]]; then
        echo "Experiment name contains 'splat'. Assuming splat experiment."
        ns-train splatfacto --data $train_dir --output_dir $model_dir --vis wandb --experiment_name $exp_name
    else
        echo "Experiment name must contain 'splat' or 'nerf'"
        exit 1
    fi
fi

# Extract the model config and render the model
model_config=$(find_latest_config "${model_dir}/${exp_name}")
ns-render camera-path --load-config $model_config --camera-path-filename $abs_camera_path --output-path $render_dir --output-format images

# Evaluate the model
./eval_pipeline.py $render_dir $result_file $exp_name
if [ $? -ne 0 ]; then
    echo "eval_pipeline.py failed for experiment ${exp_name}. Run the script manually to debug."
    exit 1
fi
