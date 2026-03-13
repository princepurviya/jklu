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

def detect_misplaced_objects(diff_image: np.ndarray, frame: np.ndarray, min_area: int = 5000):
    """
    Finds large contours in the SSIM difference heatmap and draws bounding boxes
    around them to detect misplaced exhibits/objects.
    """
    annotated = frame.copy()
    count = 0
    
    # Extract the Red channel from the COLORMAP_JET heatmap.
    # High difference values map to yellow/red (high Red channel).
    if len(diff_image.shape) == 3 and diff_image.shape[2] == 3:
        R_channel = diff_image[:, :, 2]
    else:
        R_channel = diff_image
        
    # Threshold to create a binary mask of high-difference regions
    _, thresh = cv2.threshold(R_channel, 150, 255, cv2.THRESH_BINARY)
    
    # Morphological opening to remove small noise
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area: # Detect only large objects
            x, y, w, h = cv2.boundingRect(cnt)
            # Draw red bounding box
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 0, 255), 3)
            # Label as misplaced object
            cv2.putText(annotated, "MISPLACED OBJECT", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            count += 1
            
    return annotated, count
