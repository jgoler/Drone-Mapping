"""
Given frame numbers selected as keyframes, retrieve frames from the processed data folder created by Colmap.
"""

import json
import os
import shutil
from datetime import datetime
from utils import get_config


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


def create_output_json(new_data, output_json_folder):
    # Make sure the output_json_folder exists and is a directory
    assert os.path.isdir(output_json_folder), (
        f"Output folder {output_json_folder} does not exist or is not a directory."
    )

    # Check if there is an existing transforms.json file in the output_json_folder. Rename it if so.
    output_json_path = os.path.join(output_json_folder, "transforms.json")
    if os.path.exists(output_json_path):
        current_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"transforms_{current_date_time}.json"
        os.rename(output_json_path, os.path.join(os.path.dirname(output_json_path), new_name))

    # Write the new data to the output_json_path
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


if __name__ == "__main__":
    # Example usage
    config = get_config()
    original_json_path = config["org_transforms"]
    selected_frame_numbers = [20 * i for i in range(1, 191)]  # List of frame numbers to extract
    output_json_folder = config["PROCESSED"]

    new_data = get_frames_data(original_json_path, selected_frame_numbers)
    create_output_json(new_data, output_json_folder)
