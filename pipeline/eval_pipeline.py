#!/usr/bin/env python
"""
Pipeline for evaluating NeRF / Gaussian Splat renders using PSNR, SSIM, and LPIPS.
"""

import numpy as np
import os
import argparse
from utils import get_config
import traceback

# Import metrics for calculations
from skimage.metrics import structural_similarity as ssim
from skimage.io import imread
import lpips
import torch


def load_images_from_folder(folder, frame_numbers=None):
    images = []
    image_nums = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = imread(os.path.join(folder, filename))
            if img is not None:
                images.append(img)
                image_nums.append(int(filename.split("_")[-1].split(".")[0]))
    images, image_nums = np.array(images), np.array(image_nums)
    if frame_numbers is not None:
        indices = np.where(np.isin(image_nums, frame_numbers))[0]
        images = images[indices]
    return images


def normalize_images(images):
    if np.max(images) > 1.0:
        images = images / 255.0
    return images


def calculate_lpips(pred, gt):
    # Initialize LPIPS model
    loss_fn = lpips.LPIPS(net="alex")

    # Convert images to tensor and normalize to [-1, 1]
    pred_tensor = (torch.tensor(pred, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) * 2) - 1
    gt_tensor = (torch.tensor(gt, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) * 2) - 1

    # Calculate LPIPS score
    lpips_score = loss_fn(pred_tensor, gt_tensor).item()

    return lpips_score


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Evaluate NeRF / Gaussian Splat renders.")
    parser.add_argument("model_renders", type=str, help="Path to the model renders folder")
    parser.add_argument("output_csv", type=str, help="Path to the output csv")
    parser.add_argument("experiment_name", type=str, help="Name of the experiment")
    args = parser.parse_args()

    # Load config.yaml variables
    config = get_config()

    # Get the keyframe numbers for the experiment. For now, we'll hard code the frame numbers
    selected_frame_numbers = [i for i in range(741, 973)]

    # Load images
    print("Loading images...")
    pred_images = load_images_from_folder(args.model_renders, frame_numbers=None)
    eval_images_path = os.path.join(config["proj_dir"], config["eval_images"])
    eval_images = load_images_from_folder(eval_images_path, frame_numbers=selected_frame_numbers)
    print(pred_images.shape, eval_images.shape)

    # Normalize images if they are not already normalized
    pred_images = normalize_images(pred_images)
    eval_images = normalize_images(eval_images)

    # Check if images are normalized
    assert np.max(pred_images) <= 1.0 and np.min(pred_images) >= 0.0, (
        "Predicted image is not normalized to [0, 1]"
    )
    assert np.max(eval_images) <= 1.0 and np.min(eval_images) >= 0.0, (
        "Ground truth image is not normalized to [0, 1]"
    )

    print("Calculating PSNR scores...")
    # Vectorized PSNR calculation
    mse = np.mean((pred_images - eval_images) ** 2, axis=(1, 2, 3))
    psnr_scores = 10 * np.log10(1.0 / mse)

    print("Calculating SSIM scores...")
    # Vectorized SSIM calculation
    ssim_scores = np.array(
        [
            ssim(pred, gt, channel_axis=-1, data_range=1.0)
            for pred, gt in zip(pred_images, eval_images)
        ]
    )

    print("Calculating LPIPS scores...")
    # Batch LPIPS calculation
    lpips_scores = np.array(
        [calculate_lpips(pred, gt) for pred, gt in zip(pred_images, eval_images)]
    )

    data = np.vstack((psnr_scores, ssim_scores, lpips_scores)).T

    # Create directory for output_csv if it does not exist
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    np.savetxt(
        args.output_csv, data, delimiter=",", fmt="%.2f", header="PSNR,SSIM,LPIPS", comments=""
    )

    print(f"Saved evaluation results to {args.output_csv}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred during evaluation: {e}")
        traceback.print_exc()
        exit(1)
