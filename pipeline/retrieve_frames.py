"""
Given frame numbers selected as keyframes, retrieve frames from the processed data folder created by Colmap.
"""

import json
import os
import shutil


def extract_frames(original_json_path, selected_frame_numbers, output_json_path):
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

    # Write the new transforms.json file
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
    original_json_path = "/home/navlab/NeRF/drone_mapping/Drone-Mapping/data/processed/pepperwood_preserve/100p/transforms.json"
    selected_frame_numbers = [5 * i for i in range(100)]  # List of frame numbers to extract
    output_json_path = "/home/navlab/NeRF/drone_mapping/test_folder/colmap_sample/transforms.json"

    skip_json = True  # Set to True if you only want to copy the images and not modify the json file
    if not skip_json:
        extract_frames(original_json_path, selected_frame_numbers, output_json_path)

    original_images_folder = "/home/navlab/NeRF/drone_mapping/Drone-Mapping/data/processed/pepperwood_preserve/100p/images"
    destination_folder = "/home/navlab/NeRF/drone_mapping/test_folder/colmap_sample/images"
    copy_selected_images(original_images_folder, selected_frame_numbers, destination_folder)
