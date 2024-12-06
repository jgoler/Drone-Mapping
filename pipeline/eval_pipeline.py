#!/usr/bin/env python
"""
Pipeline for evaluating NeRF / Gaussian Splat renders using PSNR, SSIM, and LPIPS.
"""

import numpy as np
import os
import argparse

# from eval_metrics import calculate_ssim
from skimage.metrics import structural_similarity as ssim
from skimage.io import imread


def load_images_from_folder(folder):
    images = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = imread(os.path.join(folder, filename))
            if img is not None:
                images.append(img)
    return np.array(images)


def normalize_images(images):
    if np.max(images) > 1.0:
        images = images / 255.0
    return images


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Evaluate NeRF / Gaussian Splat renders.")
    parser.add_argument("model_renders", type=str, help="Path to the model renders folder")
    parser.add_argument("gt_renders", type=str, help="Path to the ground-truth renders folder")
    parser.add_argument("output_csv", type=str, help="Path to the output csv")
    args = parser.parse_args()

    # Load images
    print("Loading images...")
    pred_images = load_images_from_folder(args.model_renders)
    gt_images = load_images_from_folder(args.gt_renders)
    print(pred_images.shape, gt_images.shape)

    # Normalize images if they are not already normalized
    pred_images = normalize_images(pred_images)
    gt_images = normalize_images(gt_images)

    # Check if images are normalized
    assert (
        np.max(pred_images) <= 1.0 and np.min(pred_images) >= 0.0
    ), "Predicted image is not normalized to [0, 1]"
    assert (
        np.max(gt_images) <= 1.0 and np.min(gt_images) >= 0.0
    ), "Ground truth image is not normalized to [0, 1]"

    print("Calculating PSNR scores...")
    # Vectorized PSNR calculation
    mse = np.mean((pred_images - gt_images) ** 2, axis=(1, 2, 3))
    psnr_scores = 10 * np.log10(1.0 / mse)

    print("Calculating SSIM scores...")
    # Vectorized SSIM calculation
    ssim_scores = np.array(
        [
            ssim(pred, gt, channel_axis=-1, data_range=1.0)
            for pred, gt in zip(pred_images, gt_images)
        ]
    )

    print("We'll skip LPIPS calculation for now.")
    # Batch LPIPS calculation
    # lpips_scores = np.array([calculate_lpips(pred, gt) for pred, gt in zip(pred_images, gt_images)])

    data = np.vstack((psnr_scores, ssim_scores)).T

    # Create directory for output_csv if it does not exist
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    np.savetxt(args.output_csv, data, delimiter=",", fmt="%.2f", header="PSNR,SSIM", comments="")

    print(f"Saved evaluation results to {args.output_csv}")


if __name__ == "__main__":
    main()
