#!/usr/bin/env python
"""
Pipeline for evaluating NeRF / Gaussian Splat renders using PSNR, SSIM, and LPIPS.

*Note: we discovered our camera path was reversed from eval images, so added functionality to reverse predicted images here.*
"""

import numpy as np
import os
import argparse
from utils import get_config
import traceback

# Import metrics for calculations
from skimage.io import imread, imsave
import lpips
from pytorch_msssim import ssim
import torch
from concurrent.futures import ThreadPoolExecutor


def load_images_from_folder(folder, frame_numbers=None, reverse=False, return_frame_nums=False):
    images = []
    image_nums = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = imread(os.path.join(folder, filename))
            if img is not None:
                images.append(img)
                try:
                    image_nums.append(int(filename.split("_")[-1].split(".")[0]))
                except ValueError:
                    print(f"Warning: Could not parse frame number from filename: {filename}")
                    image_nums.append(-1)
    images, image_nums = np.array(images), np.array(image_nums)
    if frame_numbers is not None:
        indices = np.where(np.isin(image_nums, frame_numbers))[0]
        images = images[indices]
        image_nums = image_nums[indices]
    if reverse:
        images = images[::-1]
        image_nums = image_nums[::-1]
    if return_frame_nums:
        return images, image_nums
    return images


def normalize_images(images):
    if np.max(images) > 1.0:
        images = images / 255.0
    return images


def save_comparison_images(pred_images, eval_images, output_folder, frame_nums=None):
    """Save side-by-side comparison images (predicted | ground truth) for debugging."""
    os.makedirs(output_folder, exist_ok=True)

    for i in range(len(pred_images)):
        pred = pred_images[i]
        gt = eval_images[i]

        # Concatenate horizontally: predicted on left, ground truth on right
        comparison = np.concatenate([pred, gt], axis=1)

        # Convert to uint8 if normalized
        if comparison.max() <= 1.0:
            comparison = (comparison * 255).astype(np.uint8)

        # Use frame number if available, otherwise use index
        if frame_nums is not None:
            filename = f"comparison_{frame_nums[i]:04d}.png"
        else:
            filename = f"comparison_{i:04d}.png"

        imsave(os.path.join(output_folder, filename), comparison)

    print(f"Saved {len(pred_images)} comparison images to {output_folder}")


# ---- Create LPIPS model on each GPU ----
def create_models():
    models = {}
    for i in range(torch.cuda.device_count()):
        device = torch.device(f"cuda:{i}")
        model = lpips.LPIPS(net="alex").to(device)
        model.eval()
        models[i] = model
    return models


MODELS = create_models()


# ---- LPIPS evaluate a chunk on a specific GPU ----
@torch.no_grad()
def eval_chunk_on_gpu(pred_chunk, gt_chunk, gpu_id, is_lpips):
    device = torch.device(f"cuda:{gpu_id}")
    model = MODELS[gpu_id]

    pred = torch.tensor(pred_chunk).permute(0, 3, 1, 2).float()  # NHWC→NCHW
    gt = torch.tensor(gt_chunk).permute(0, 3, 1, 2).float()

    if is_lpips:
        pred = pred * 2 - 1
        gt = gt * 2 - 1

    pred = pred.to(device, non_blocking=True)
    gt = gt.to(device, non_blocking=True)

    with torch.cuda.amp.autocast(dtype=torch.float16):  # type: ignore
        if is_lpips:
            scores = model(pred, gt).view(-1)
        else:
            # Assume metric is ssim then
            scores = ssim(pred, gt, data_range=1.0, size_average=False).view(-1)

    torch.cuda.empty_cache()
    return scores.cpu()


def parallel_eval(pred, gt, chunk_size=2, is_lpips=True):
    futures = []
    results = []

    num_gpus = torch.cuda.device_count()
    executor = ThreadPoolExecutor(max_workers=num_gpus)

    i = 0
    gpu_id = 0

    while i < len(pred):
        p = pred[i : i + chunk_size]
        g = gt[i : i + chunk_size]

        futures.append(executor.submit(eval_chunk_on_gpu, p, g, gpu_id, is_lpips))

        gpu_id = (gpu_id + 1) % num_gpus
        i += chunk_size

    for f in futures:
        results.append(f.result())

    return torch.cat(results)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Evaluate NeRF / Gaussian Splat renders.")
    parser.add_argument("model_renders", type=str, help="Path to the model renders folder")
    parser.add_argument("output_csv", type=str, help="Path to the output csv")
    parser.add_argument("experiment_name", type=str, help="Name of the experiment")
    parser.add_argument(
        "--save_comparisons",
        type=str,
        default=None,
        help="Path to save side-by-side comparison images for debugging",
    )
    args = parser.parse_args()

    # Load config.yaml variables
    config = get_config()

    # Get the keyframe numbers for the experiment. For now, we'll hard code the frame numbers
    selected_frame_numbers = [i for i in range(741, 973)]

    # Load images
    print("Loading images...")
    # Reversing the predicted images to match eval images order
    pred_images, pred_frame_nums = load_images_from_folder(
        args.model_renders, frame_numbers=None, reverse=True, return_frame_nums=True
    )
    eval_images_path = os.path.join(config["proj_dir"], config["eval_images"])
    eval_images, eval_frame_nums = load_images_from_folder(
        eval_images_path, frame_numbers=selected_frame_numbers, return_frame_nums=True
    )
    print(f"Render path: {args.model_renders}")
    print(f"Eval images path: {eval_images_path}")
    print(f"Predicted images shape: {pred_images.shape}")
    print(f"Eval images shape: {eval_images.shape}")

    # Validation checks
    if len(pred_images) != len(eval_images):
        raise ValueError(
            f"Image count mismatch: {len(pred_images)} predicted images vs {len(eval_images)} eval images. "
            "Ensure the render and eval folders contain the same number of frames."
        )

    if pred_images.shape[1:] != eval_images.shape[1:]:
        raise ValueError(
            f"Image resolution mismatch: predicted {pred_images.shape[1:]} vs eval {eval_images.shape[1:]}. "
            "Images must have the same dimensions."
        )

    # Check frame number alignment (after reversing pred)
    if not np.array_equal(
        pred_frame_nums, eval_frame_nums
    ):  # I don't know if we would expect this to be equal, though, because they come from different folders
        print(f"Warning: Frame numbers do not match after alignment!")
        print(f"  Predicted frame nums (first 5): {pred_frame_nums[:5]}")
        print(f"  Eval frame nums (first 5): {eval_frame_nums[:5]}")
        print(f"  Predicted frame nums (last 5): {pred_frame_nums[-5:]}")
        print(f"  Eval frame nums (last 5): {eval_frame_nums[-5:]}")

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

    # Save comparison images for debugging if requested
    if args.save_comparisons:
        print("Saving comparison images...")
        save_comparison_images(pred_images, eval_images, args.save_comparisons, eval_frame_nums)

    # # View 100th image for sanity check
    # import matplotlib.pyplot as plt

    # idx_to_plot = [99, 100, 101]

    # for i in range(len(idx_to_plot)):
    #     plt.subplot(3, 3, i + 1)
    #     plt.imshow(pred_images[idx_to_plot[i]])
    #     plt.title(f"Predicted Image - {idx_to_plot[i]}th")
    #     plt.axis("off")

    #     plt.subplot(3, 3, 3 + i + 1)
    #     plt.imshow(eval_images[idx_to_plot[i]])
    #     plt.title(f"Eval Image - {idx_to_plot[i]}th")
    #     plt.axis("off")

    #     plt.subplot(3, 3, 6 + i + 1)
    #     plt.imshow(pred_images[idx_to_plot[i]] - eval_images[idx_to_plot[i]])
    #     plt.title(f"Difference Image - {idx_to_plot[i]}th")
    #     plt.axis("off")

    # plt.show()

    print("Calculating PSNR scores...")
    # Vectorized PSNR calculation
    mse = np.mean((pred_images - eval_images) ** 2, axis=(1, 2, 3))
    psnr_scores = 10 * np.log10(1.0 / mse)

    print("Calculating SSIM scores...")
    # GPU accelerated SSIM calculation
    ssim_scores = parallel_eval(pred_images, eval_images, chunk_size=4, is_lpips=False)
    ssim_scores = ssim_scores.cpu().numpy()

    print("Calculating LPIPS scores...")
    lpips_scores_tensor = parallel_eval(pred_images, eval_images, chunk_size=4, is_lpips=True)
    lpips_scores = lpips_scores_tensor.cpu().numpy()

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
