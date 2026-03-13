"""
comparator.py — Baseline vs current image comparison using SSIM.
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def compute_ssim(baseline: np.ndarray, current: np.ndarray):
    """
    Compute the Structural Similarity Index between two images.
    Both images are resized to the same dimensions and converted to grayscale.
    Returns:
        score    : float in [0, 1]  (1 = identical)
        diff_img : absolute difference heatmap (BGR, coloured)
    """
    h, w = baseline.shape[:2]
    current_resized = cv2.resize(current, (w, h))

    gray_base = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(current_resized, cv2.COLOR_BGR2GRAY)

    score, diff = ssim(gray_base, gray_curr, full=True)
    # diff is float64 in [0,1] — convert to uint8
    diff = (diff * 255).astype(np.uint8)

    # colour-map the diff so changes pop out
    diff_coloured = cv2.applyColorMap(255 - diff, cv2.COLORMAP_JET)

    return round(score, 4), diff_coloured


def compare_images(baseline: np.ndarray, current: np.ndarray,
                   threshold: float = 0.85):
    """
    High-level comparison returning a result dict.
    """
    score, diff_img = compute_ssim(baseline, current)
    damage_detected = score < threshold

    return {
        "ssim_score": score,
        "threshold": threshold,
        "damage_detected": damage_detected,
        "diff_image": diff_img,
    }
