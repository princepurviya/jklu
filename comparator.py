"""
comparator.py — Baseline vs current image comparison using SSIM.
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def _preprocess_for_diff(image: np.ndarray, blur_ksize: int = 21) -> np.ndarray:
    """Convert frame to grayscale and denoise with Gaussian blur."""
    if blur_ksize % 2 == 0:
        blur_ksize += 1
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)


def _extract_changed_regions(binary_mask: np.ndarray, min_change_area: int = 800):
    """Return contours and total changed area after area filtering."""
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    kept_contours = []
    total_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_change_area:
            continue
        kept_contours.append(cnt)
        total_area += int(area)

    return kept_contours, total_area


def compute_ssim(baseline: np.ndarray, current: np.ndarray, blur_ksize: int = 21):
    """
    Compute the Structural Similarity Index between two images.
    Both images are resized to the same dimensions and converted to grayscale.
    Returns:
        score    : float in [0, 1]  (1 = identical)
        diff_img : absolute difference heatmap (BGR, coloured)
    """
    h, w = baseline.shape[:2]
    current_resized = cv2.resize(current, (w, h))

    gray_base = _preprocess_for_diff(baseline, blur_ksize=blur_ksize)
    gray_curr = _preprocess_for_diff(current_resized, blur_ksize=blur_ksize)

    score, diff = ssim(gray_base, gray_curr, full=True)
    # diff is float64 in [0,1] — convert to uint8
    diff = (diff * 255).astype(np.uint8)

    # colour-map the diff so changes pop out
    diff_coloured = cv2.applyColorMap(255 - diff, cv2.COLORMAP_JET)

    return round(score, 4), diff_coloured, (255 - diff)


def compute_absdiff(baseline: np.ndarray, current: np.ndarray, blur_ksize: int = 21):
    """Compute absolute grayscale difference after denoising."""
    h, w = baseline.shape[:2]
    current_resized = cv2.resize(current, (w, h))

    gray_base = _preprocess_for_diff(baseline, blur_ksize=blur_ksize)
    gray_curr = _preprocess_for_diff(current_resized, blur_ksize=blur_ksize)

    abs_diff = cv2.absdiff(gray_base, gray_curr)
    score = 1.0 - (float(np.mean(abs_diff)) / 255.0)
    diff_coloured = cv2.applyColorMap(abs_diff, cv2.COLORMAP_JET)
    return round(max(0.0, min(1.0, score)), 4), diff_coloured, abs_diff


def compare_images(baseline: np.ndarray, current: np.ndarray,
                   threshold: float = 0.85,
                   method: str = "absdiff",
                   blur_ksize: int = 21,
                   min_change_area: int = 2000,
                   diff_threshold: int = 40):
    """
    High-level comparison returning a result dict.
    """
    if method == "absdiff":
        score, diff_img, diff_gray = compute_absdiff(baseline, current, blur_ksize=blur_ksize)
    else:
        score, diff_img, diff_gray = compute_ssim(baseline, current, blur_ksize=blur_ksize)

    _, binary_mask = cv2.threshold(diff_gray, diff_threshold, 255, cv2.THRESH_BINARY)
    binary_mask = cv2.dilate(binary_mask, None, iterations=2)

    changed_contours, changed_area = _extract_changed_regions(binary_mask, min_change_area=min_change_area)
    if method == "ssim":
        score_indicates_change = score < threshold
        damage_detected = score_indicates_change and (changed_area > 0)
    else:
        damage_detected = changed_area > 0

    return {
        "ssim_score": score,
        "threshold": threshold,
        "damage_detected": damage_detected,
        "diff_image": diff_img,
        "binary_mask": binary_mask,
        "changed_contours": changed_contours,
        "changed_area": changed_area,
        "method": method,
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
