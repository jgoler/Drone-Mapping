"""
Pipeline for evaluating NeRF / Gaussian Splat renders using PSNR, SSIM, and LPIPS.
"""

import numpy as np
from eval_metrics import calculate_psnr, calculate_ssim, calculate_lpips


def main():
    # Load images
    pred_images = np.load("pred_images.npy")
    gt_images = np.load("gt_images.npy")

    psnr_scores = []
    ssim_scores = []
    lpips_scores = []

    for pred, gt in zip(pred_images, gt_images):
        psnr_scores.append(calculate_psnr(pred, gt))
        ssim_scores.append(calculate_ssim(pred, gt))
        lpips_scores.append(calculate_lpips(pred, gt))

    # Average scores across views
    mean_psnr = np.mean(psnr_scores)
    mean_ssim = np.mean(ssim_scores)
    mean_lpips = np.mean(lpips_scores)

    print(f"Mean PSNR: {mean_psnr}")
    print(f"Mean SSIM: {mean_ssim}")
    print(f"Mean LPIPS: {mean_lpips}")


if __name__ == "__main__":
    main()
