import numpy as np
from skimage.metrics import structural_similarity as ssim
import lpips
import torch


def calculate_psnr(pred, gt):
    """
    Calculate the Peak Signal-to-Noise Ratio (PSNR) between two images.
    Requires normalized images in the range [0, 1].
    """
    mse = np.mean((pred - gt) ** 2)
    if mse == 0:
        return float("inf")  # Perfect match
    max_pixel = 1.0  # Assuming images are normalized to [0, 1]
    return 10 * np.log10(max_pixel**2 / mse)


def calculate_ssim(pred, gt):
    """
    Calculate the Structural Similarity Index (SSIM) between two images.
    Requires normalized images in the range [0, 1].
    """
    return ssim(pred, gt, channel_axis=-1, data_range=1.0)


# Initialize the LPIPS model
LOSS_FN = lpips.LPIPS(net="vgg")  # 'vgg' or 'alex'


def calculate_lpips(pred, gt):
    """
    Calculate the Learned Perceptual Image Patch Similarity (LPIPS) between two images.
    Requires normalized images in the range [0, 1].
    """
    global LOSS_FN

    # Convert images to tensors and ensure they are scaled to [-1, 1]
    pred_tensor = torch.tensor(pred, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) * 2 - 1
    gt_tensor = torch.tensor(gt, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) * 2 - 1

    return LOSS_FN(pred_tensor, gt_tensor).item()
