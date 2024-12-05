#!/usr/bin/env python
"""
Pipeline for evaluating NeRF / Gaussian Splat renders using PSNR, SSIM, and LPIPS.
"""

import numpy as np
import os
import argparse
from eval_metrics import calculate_psnr, calculate_ssim, calculate_lpips
from skimage.io import imread


def load_images_from_folder(folder):
    images = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = imread(os.path.join(folder, filename))
            if img is not None:
                images.append(img)
    return np.array(images)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Evaluate NeRF / Gaussian Splat renders.")
    parser.add_argument("model_renders", type=str, help="Path to the model renders folder")
    parser.add_argument("gt_renders", type=str, help="Path to the ground-truth renders folder")
    parser.add_argument("output_csv", type=str, help="Path to the output csv")
    args = parser.parse_args()

    # Load images
    pred_images = load_images_from_folder(args.model_renders)
    gt_images = load_images_from_folder(args.gt_renders)
    print(pred_images.shape, gt_images.shape)

    psnr_scores = []
    ssim_scores = []
    lpips_scores = []

    cnt = 0
    for pred, gt in zip(pred_images, gt_images):
        print("Processing image", cnt)
        psnr_scores.append(calculate_psnr(pred, gt))
        ssim_scores.append(calculate_ssim(pred, gt))
        lpips_scores.append(calculate_lpips(pred, gt))
        cnt += 1

    data = np.vstack((psnr_scores, ssim_scores, lpips_scores)).T

    np.savetxt(
        args.output_csv, data, delimiter=",", fmt="%.2f", header="PSNR,SSIM,LPIPS", comments=""
    )

    print(f"Saved evaluation results to {args.output_csv}")


if __name__ == "__main__":
    main()
