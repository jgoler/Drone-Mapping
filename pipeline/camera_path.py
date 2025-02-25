#!/usr/bin/env python
"""
Create Camera Path json based on data in transforms.json file.
"""

import json
import os
import numpy as np
from utils import get_config
from retrieve_frames import get_frames_data


def create_camera_path(data, output_json_path):
    """
    Create a camera path json file based on the data extracted from the original transforms.json file.
    """
    # Assert that required keys exist in data
    required_keys = ["w", "h", "fl_y", "frames"]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"Key '{key}' is missing from frames transform data")

    camera_path = dict()

    # Set the camera path attributes
    camera_path["camera_type"] = "perspective"
    camera_path["render_height"] = float(data["h"])
    camera_path["render_width"] = float(data["w"])
    camera_path["fps"] = 30.0
    camera_path["seconds"] = 6.0
    camera_path["is_cycle"] = False
    camera_path["smoothness_value"] = 0.0
    camera_path["default_fov"] = 2 * np.arctan(camera_path["render_height"] / (2 * data["fl_y"]))
    camera_path["default_transition_sec"] = 2.0
    # Aspect ratio (use for computing frames)
    aspect = camera_path["render_width"] / camera_path["render_height"]

    # Now, create the transfroms for each frame
    camera_path["camera_path"] = []
    for frame in data["frames"]:
        frame_info = dict()
        frame_info["camera_to_world"] = np.array(frame["transform_matrix"]).flatten().tolist()
        frame_info["fov"] = camera_path["default_fov"]
        frame_info["aspect"] = aspect
        camera_path["camera_path"].append(frame_info)

    # Ensure the output folder exists
    assert os.path.exists(os.path.dirname(output_json_path)), (
        f"Output folder '{os.path.dirname(output_json_path)}' d.n.e., plz create it."
    )
    # Avoid overwriting existing files
    if os.path.exists(output_json_path):
        print(f"Warning: {output_json_path} already exists. Exiting to prevent overwriting.")
        return

    # Write the new data to the output_json_path
    with open(output_json_path, "w") as f:
        json.dump(camera_path, f, indent=4)


if __name__ == "__main__":
    config = get_config()
    selected_frame_numbers = [i for i in range(741, 973)]
    org_json_path = config["full_transforms"]
    output_json_path = (
        "/home/navlab/NeRF/drone_mapping/Drone-Mapping/transforms/camera_paths/lake_lag_spiral.json"
    )

    # Extract the frames that match the selected frame numbers, along with all other data
    frames_data = get_frames_data(org_json_path, selected_frame_numbers)
    # Create the camera path and write it to json
    create_camera_path(frames_data, output_json_path)
