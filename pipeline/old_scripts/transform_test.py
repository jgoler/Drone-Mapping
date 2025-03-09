#!/usr/bin/env python3
import torch
import numpy as np
import json
import pathlib


if __name__ == "__main__":
    camera_path_file = "/home/navlab/NeRF/drone_mapping/data/lake_lag/processed/camera_paths/2025-03-05-14-54-05.json"
    dataparser_file = "/home/navlab/NeRF/drone_mapping/10p_splatfacto_lake_lag/10p_splatfacto_lake_lag/splatfacto/2025-03-04_135710/dataparser_transforms.json"
    dataparser_dir = pathlib.Path(dataparser_file).parent
    with open(dataparser_file, "r") as f:
        data = json.load(f)
    applied_scale = data["scale"]
    applied_transform = torch.tensor(data["transform"], dtype=torch.float32)
    with open(camera_path_file, "r") as f:
        camera_path = json.load(f)

    pose = torch.tensor(camera_path["keyframes"][0]["matrix"], dtype=torch.float32)
    pose = pose.reshape(4, 4)
    assert torch.allclose(
        pose[3, :], torch.tensor([0, 0, 0, 1], dtype=pose.dtype, device=pose.device)
    ), "Last row of pose matrix is not [0, 0, 0, 1]"

    pose[:3, 3] /= applied_scale
    inv_transform = torch.linalg.inv(
        torch.cat(
            (
                applied_transform,
                torch.tensor(
                    [[0, 0, 0, 1]], dtype=applied_transform.dtype, device=applied_transform.device
                ),
            ),
            0,
        )
    )

    # pose = torch.matmul(inv_transform, pose)
    pose = inv_transform @ pose
    # pose = torch.matmul(pose, inv_transform)
    # pose = torch.einsum("ij,jk->ik", inv_transform, pose)

    # pose[..., 0:3, 1:3] *= -1

    pose_file = dataparser_dir / "test_pose.json"
    with open(pose_file, "w") as f:
        json.dump(pose.tolist(), f, indent=4)
    print(f"Pose matrix written to {pose_file}")
    print(pose)
