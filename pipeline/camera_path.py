#!/usr/bin/env python
"""
Create Camera Path json based on data in transforms.json file.
"""

import json
import os
import numpy as np
from utils import get_config
from retrieve_frames import get_frames_data


def invert_transformation(matrix):
    """Invert a 4x4 transformation matrix."""
    R = np.array(matrix[:3, :3])
    t = np.array(matrix[:3, 3])
    R_inv = R.T
    t_inv = -R.T @ t
    matrix_inv = np.eye(4)
    matrix_inv[:3, :3] = R_inv
    matrix_inv[:3, 3] = t_inv
    return matrix_inv


def create_camera_path(org_json_path, selected_frame_numbers, w_to_rf_path, output_json_path):
    """
    Create a camera path json file based on the data extracted from the original transforms.json file.
    """

    # Extract the frames that match the selected frame numbers, along with all other data
    data = get_frames_data(org_json_path, selected_frame_numbers)

    # Get transforms data from the world to the radiance field coordinates
    with open(w_to_rf_path, "r") as f:
        w_to_rf_data = json.load(f)

    # Build the transformation matrix from world to radiance field coordinates
    assert "transform" in w_to_rf_data, "Transformation matrix not found in w_to_rf data"
    assert "scale" in w_to_rf_data, "Scale not found in w_to_rf data"
    T_w_rf = np.array(w_to_rf_data["transform"])
    assert T_w_rf.shape == (3, 4), "Transformation data is not 3x4"
    T_w_rf = np.vstack((T_w_rf, np.array([0, 0, 0, 1])))

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
    camera_path["default_fov"] = (
        2 * np.arctan(camera_path["render_height"] / (2 * data["fl_y"])) * 180 / np.pi
    )
    camera_path["default_transition_sec"] = 2.0
    # Aspect ratio (use for computing frames)
    aspect = camera_path["render_width"] / camera_path["render_height"]

    # Now, create the transfroms for each frame
    camera_path["camera_path"] = []
    for frame in data["frames"]:
        frame_info = dict()
        T_w_c = np.array(frame["transform_matrix"])
        T_w_c[1], T_w_c[2] = T_w_c[2].copy(), T_w_c[1].copy()
        T_w_c[1] = [-x for x in T_w_c[1]]
        T_c_rf = T_w_rf @ T_w_c
        T_c_rf[:3, 3] *= w_to_rf_data["scale"]
        # print(T_c_rf)
        frame_info["camera_to_world"] = T_c_rf.flatten().tolist()
        frame_info["fov"] = camera_path["default_fov"]
        frame_info["aspect"] = aspect
        camera_path["camera_path"].append(frame_info)

    # Ensure the output folder exists
    assert os.path.exists(os.path.dirname(output_json_path)), (
        f"Output folder '{os.path.dirname(output_json_path)}' d.n.e., plz create it."
    )
    # Warning overwriting existing files
    if os.path.exists(output_json_path):
        print(f"Warning: {output_json_path} already exists. Overwriting it.")

    # Write the new data to the output_json_path
    with open(output_json_path, "w") as f:
        json.dump(camera_path, f, indent=4)


if __name__ == "__main__":
    config = get_config()
    selected_frame_numbers = [i for i in range(741, 973)]
    org_json_path = config["full_transforms"]
    output_json_path = (
        "/home/navlab/NeRF/drone_mapping/data/lake_lag/processed/camera_paths/sample_eval_path.json"
    )
    # This file (dataparser_transforms.json in model folder) converts colmap coordinates to NeRF coordinates
    w_to_rf_path = "/home/navlab/NeRF/drone_mapping/10p_splatfacto_lake_lag/10p_splatfacto_lake_lag/splatfacto/2025-03-04_135710/dataparser_transforms.json"

    # Create the camera path and write it to json
    create_camera_path(org_json_path, selected_frame_numbers, w_to_rf_path, output_json_path)
