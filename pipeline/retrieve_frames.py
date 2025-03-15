#!/usr/bin/env python
"""
Given frame numbers selected as keyframes, retrieve frames from the processed data folder created by Colmap.
"""

import json
import os
import shutil
from utils import get_config
import argparse


def get_frames_data(original_json_path, selected_frame_numbers):
    """
    Extracts the frames with the selected frame numbers from the original transforms.json file and returns the new data
    as a dictionary. The new data can be written to a new file using the output_json_path.
    """
    # Read the original transforms.json file
    with open(original_json_path, "r") as f:
        data = json.load(f)

    # Convert selected frame numbers to strings with leading zeros
    selected_frame_numbers_str = [f"{num:05d}" for num in selected_frame_numbers]

    # Extract the frames that match the selected frame numbers
    selected_frames = [
        frame
        for frame in data["frames"]
        if frame["file_path"].split("/")[-1].split(".")[0].split("_")[-1]
        in selected_frame_numbers_str
    ]

    # Create a new dictionary with the same attributes as the original, but with the selected frames
    new_data = {key: value for key, value in data.items() if key != "frames"}
    new_data["frames"] = selected_frames

    return new_data


def create_output_json(new_data, output_json_path):
    folder = os.path.dirname(output_json_path)
    assert os.path.exists(folder), f"Output folder '{folder}' d.n.e., plz create it."

    # Write the new data to the output_json_path. Will overwrite existing file.
    with open(output_json_path, "w") as f:
        json.dump(new_data, f, indent=4)


def copy_selected_images(original_images_folder, selected_frame_numbers, destination_folder):
    # Convert selected frame numbers to strings with leading zeros
    selected_frame_numbers_str = [f"{num:05d}" for num in selected_frame_numbers]

    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Copy the selected images to the destination folder
    for frame_number in selected_frame_numbers_str:
        src_file = os.path.join(original_images_folder, f"frame_{frame_number}.jpg")
        dst_file = os.path.join(destination_folder, f"frame_{frame_number}.jpg")
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)
        else:
            print(f"Warning: {src_file} does not exist and will not be copied.")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Write info of selected frames to json.")
    parser.add_argument("experiment_name", type=str, help="Name of the experiment")
    args = parser.parse_args()

    # Load config.yaml variables
    config = get_config()

    # Get the keyframe numbers for the experiment
    kf_num_filename = config["kf_num_files"].get(args.experiment_name)

    with open(os.path.join(config["proj_dir"], config["kf_nums_dir"], kf_num_filename), "r") as f:
        selected_frame_numbers = [int(line.strip()) for line in f]

    # Get the paths for the input and output files
    original_json_path = os.path.join(config["proj_dir"], config["full_transforms"])
    output_json_path = os.path.join(config["proj_dir"], config["processed"], "transforms.json")

    new_data = get_frames_data(original_json_path, selected_frame_numbers)
    create_output_json(new_data, output_json_path)
    print("Selected frames info written to", output_json_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    exit(0)
