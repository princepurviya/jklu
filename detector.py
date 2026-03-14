"""
detector.py — YOLOv8 object detection + advanced crack / structural-damage detection.

Three complementary methods are combined so that both obvious and subtle
cracks are caught:
  1. CLAHE-enhanced Canny edge detection  (catches fine lines)
  2. Adaptive-threshold morphology         (catches dark crack patterns)
  3. Laplacian-of-Gaussian variance        (catches texture disruptions)
"""

import cv2
import numpy as np
from ultralytics import YOLO

# ── COCO classes considered "unwanted" in a structural environment ──────────
UNWANTED_CLASSES = {
    "bottle", "cup", "fork", "knife", "spoon", "bowl",
    "handbag", "backpack", "suitcase", "umbrella",
    "cell phone", "laptop", "mouse", "keyboard",
    "book", "scissors", "teddy bear", "toothbrush",
    "sports ball", "frisbee", "skateboard", "surfboard",
    "banana", "apple", "sandwich", "pizza", "donut", "cake",
}

# ── Colours (BGR) ───────────────────────────────────────────────────────────
BOX_COLOR       = (0, 0, 255)     # red
CRACK_COLOR     = (0, 255, 255)   # yellow
CRACK_COLOR_2   = (0, 200, 255)   # orange-ish
HIGHLIGHT_COLOR = (255, 0, 255)   # magenta
TEXT_BG         = (0, 0, 0)


class DamageDetector:
    """YOLOv8 inference + multi-method structural-crack detection."""

    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.40):
        self.model = YOLO(model_path)
        self.confidence = confidence

    # ════════════════════════════════════════════════════════════════════════
    # 1.  Unwanted-object detection (YOLO)
    # ════════════════════════════════════════════════════════════════════════
    def detect_objects(self, frame: np.ndarray):
        """
        Returns:
            annotated : copy of frame with bounding boxes
            detections: list[dict] with label / confidence / bbox
        """
        scene_detections = self.detect_scene_objects(frame)
        detections = [d for d in scene_detections if d["label"] in UNWANTED_CLASSES]
        annotated = self.draw_object_detections(frame, detections)
        return annotated, detections

    def detect_scene_objects(self, frame: np.ndarray, min_confidence: float | None = None):
        """Detect all YOLO objects with centroid metadata for tracking."""
        conf_threshold = self.confidence if min_confidence is None else min_confidence
        results = self.model(frame, conf=conf_threshold, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                detections.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": (x1, y1, x2, y2),
                    "center": (cx, cy),
                })

        return detections

    @staticmethod
    def draw_object_detections(frame: np.ndarray, detections: list[dict], color=BOX_COLOR):
        """Draw provided detections with labels."""
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            label = det["label"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            tag = f"{label} {conf:.0%}"
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), TEXT_BG, -1)
            cv2.putText(annotated, tag, (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        return annotated

    # ════════════════════════════════════════════════════════════════════════
    # 2.  Edge mask computation (reusable for baseline masking)
    # ════════════════════════════════════════════════════════════════════════
    @staticmethod
    def compute_edge_mask(
        frame: np.ndarray,
        sensitivity: str = "medium",
        edge_low: int | None = None,
        edge_high: int | None = None,
    ) -> np.ndarray:
        """
        Compute the combined triple-method edge mask for a frame.
        Returns a single-channel uint8 binary mask.
        This is used both for baseline capture and real-time detection.
        """
        presets = {
            "low":    {"edge_low": 60, "edge_high": 180},
            "medium": {"edge_low": 30, "edge_high": 120},
            "high":   {"edge_low": 15, "edge_high": 80},
        }
        p = presets.get(sensitivity, presets["medium"])
        edge_low   = edge_low   or p["edge_low"]
        edge_high  = edge_high  or p["edge_high"]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Method A: CLAHE + Canny
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred_a = cv2.GaussianBlur(enhanced, (5, 5), 0)
        edges_a = cv2.Canny(blurred_a, edge_low, edge_high)

        # Method B: Adaptive threshold (dark lines)
        blurred_b = cv2.GaussianBlur(gray, (11, 11), 0)
        thresh_b = cv2.adaptiveThreshold(
            blurred_b, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=15, C=8,
        )

        # Method C: Laplacian of Gaussian (texture disruption)
        log = cv2.Laplacian(cv2.GaussianBlur(gray, (3, 3), 0), cv2.CV_64F)
        log_abs = np.uint8(np.clip(np.abs(log), 0, 255))
        _, edges_c = cv2.threshold(log_abs, 30, 255, cv2.THRESH_BINARY)

        # Combine all three masks
        combined = cv2.bitwise_or(edges_a, thresh_b)
        combined = cv2.bitwise_or(combined, edges_c)

        # Morphology: close small gaps, then thin
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        combined = cv2.dilate(combined, kernel, iterations=2)
        combined = cv2.erode(combined, kernel, iterations=1)

        return combined

    # ════════════════════════════════════════════════════════════════════════
    # 3.  Crack / structural-damage detection  (multi-method + baseline mask)
    # ════════════════════════════════════════════════════════════════════════
    @staticmethod
    def detect_cracks(
        frame: np.ndarray,
        sensitivity: str = "medium",       # "low", "medium", "high"
        edge_low: int | None = None,
        edge_high: int | None = None,
        min_area: int | None = None,
        min_aspect: float | None = None,
        baseline_edges: np.ndarray | None = None,
    ):
        """
        Multi-method crack detection with optional baseline masking.

        If baseline_edges is provided, those edges are subtracted from the
        current frame's edge mask so that only NEW cracks are detected.

        Returns:
            overlay     : frame with crack contours highlighted
            crack_found : bool
            crack_count : total significant contour regions detected
        """
        # ── presets by sensitivity ──────────────────────────────────────────
        presets = {
            "low":    {"edge_low": 60, "edge_high": 180, "min_area": 300, "min_aspect": 2.5},
            "medium": {"edge_low": 30, "edge_high": 120, "min_area": 100, "min_aspect": 1.8},
            "high":   {"edge_low": 15, "edge_high": 80,  "min_area": 40,  "min_aspect": 1.3},
        }
        p = presets.get(sensitivity, presets["medium"])
        edge_low   = edge_low   or p["edge_low"]
        edge_high  = edge_high  or p["edge_high"]
        min_area   = min_area   or p["min_area"]
        min_aspect = min_aspect or p["min_aspect"]

        # ── Compute current edge mask ──────────────────────────────────────
        combined = DamageDetector.compute_edge_mask(
            frame, sensitivity=sensitivity, edge_low=edge_low, edge_high=edge_high,
        )

        # ── Baseline subtraction: remove pre-existing cracks ───────────────
        if baseline_edges is not None:
            # Resize baseline edges to match current frame if needed
            h, w = combined.shape[:2]
            bh, bw = baseline_edges.shape[:2]
            if (bh, bw) != (h, w):
                baseline_resized = cv2.resize(baseline_edges, (w, h))
            else:
                baseline_resized = baseline_edges

            # Dilate baseline edges slightly to account for minor shifts
            dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            baseline_dilated = cv2.dilate(baseline_resized, dilate_kernel, iterations=1)

            # Subtract: only edges NOT in baseline survive
            combined = cv2.subtract(combined, baseline_dilated)

        # ── Extract and filter contours ────────────────────────────────────
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        overlay = frame.copy()
        crack_count = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            aspect = max(w, h) / (min(w, h) + 1e-5)

            # accept if elongated OR if arc-length is large relative to area
            perimeter = cv2.arcLength(cnt, True)
            compactness = (perimeter * perimeter) / (area + 1e-5)

            is_elongated = aspect >= min_aspect
            is_crack_like = compactness > 50   # long thin shape

            if is_elongated or is_crack_like:
                cv2.drawContours(overlay, [cnt], -1, CRACK_COLOR, 2)
                cv2.rectangle(overlay, (x, y), (x + w, y + h), HIGHLIGHT_COLOR, 1)
                label = f"NEW crack {area:.0f}px"
                cv2.putText(overlay, label, (x, y - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, CRACK_COLOR, 1)
                crack_count += 1

        return overlay, crack_count > 0, crack_count
