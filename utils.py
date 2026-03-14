"""
utils.py — Alert engine, file I/O helpers, drawing utilities.
"""

import os
import cv2
import numpy as np
from datetime import datetime

BASELINE_DIR = os.path.join(os.path.dirname(__file__), "baseline_images")
os.makedirs(BASELINE_DIR, exist_ok=True)


# ── Alert helpers ───────────────────────────────────────────────────────────

def trigger_alert(message: str, detections: list | None = None,
                  severity: str = "HIGH"):
    """Build a timestamped alert dict."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "severity": severity,
        "message": message,
        "detections": detections or [],
    }


# ── File I/O ────────────────────────────────────────────────────────────────

def save_baseline(image: np.ndarray, name: str = "baseline.png") -> str:
    """Save *image* to the baseline_images folder. Returns saved path."""
    path = os.path.join(BASELINE_DIR, name)
    cv2.imwrite(path, image)
    return path


def load_baseline(name: str = "baseline.png") -> np.ndarray | None:
    """Load a previously saved baseline image. Returns None if missing."""
    path = os.path.join(BASELINE_DIR, name)
    if not os.path.exists(path):
        return None
    return cv2.imread(path)


def clear_baseline(name: str = "baseline.png"):
    """Delete the saved baseline image and its edge mask from disk."""
    path = os.path.join(BASELINE_DIR, name)
    if os.path.exists(path):
        os.remove(path)
    edges_path = os.path.join(BASELINE_DIR, "baseline_edges.png")
    if os.path.exists(edges_path):
        os.remove(edges_path)


def save_baseline_edges(edges: np.ndarray, name: str = "baseline_edges.png") -> str:
    """Save baseline edge mask to disk. Returns saved path."""
    path = os.path.join(BASELINE_DIR, name)
    cv2.imwrite(path, edges)
    return path


def load_baseline_edges(name: str = "baseline_edges.png") -> np.ndarray | None:
    """Load a previously saved baseline edge mask. Returns None if missing."""
    path = os.path.join(BASELINE_DIR, name)
    if not os.path.exists(path):
        return None
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


# ── Drawing ─────────────────────────────────────────────────────────────────

def draw_detections(frame: np.ndarray, detections: list,
                    color=(0, 0, 255), thickness=2) -> np.ndarray:
    """Draw bounding boxes + labels onto *frame* (in-place)."""
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = f'{det["label"]} {det["confidence"]:.0%}'
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(frame, label, (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame
