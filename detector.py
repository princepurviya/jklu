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
        results = self.model(frame, conf=self.confidence, verbose=False)
        annotated = frame.copy()
        detections = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                conf  = float(box.conf[0])

                if label not in UNWANTED_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": (x1, y1, x2, y2),
                })

                cv2.rectangle(annotated, (x1, y1), (x2, y2), BOX_COLOR, 2)
                tag = f"{label} {conf:.0%}"
                (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), TEXT_BG, -1)
                cv2.putText(annotated, tag, (x1 + 2, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return annotated, detections

    # ════════════════════════════════════════════════════════════════════════
    # 2.  Crack / structural-damage detection  (multi-method)
    # ════════════════════════════════════════════════════════════════════════
    @staticmethod
    def detect_cracks(
        frame: np.ndarray,
        sensitivity: str = "medium",       # "low", "medium", "high"
        edge_low: int | None = None,
        edge_high: int | None = None,
        min_area: int | None = None,
        min_aspect: float | None = None,
    ):
        """
        Multi-method crack detection.

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ── Method A: CLAHE + Canny ────────────────────────────────────────
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred_a = cv2.GaussianBlur(enhanced, (5, 5), 0)
        edges_a = cv2.Canny(blurred_a, edge_low, edge_high)

        # ── Method B: Adaptive threshold (dark lines) ──────────────────────
        blurred_b = cv2.GaussianBlur(gray, (11, 11), 0)
        thresh_b = cv2.adaptiveThreshold(
            blurred_b, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=15, C=8,
        )

        # ── Method C: Laplacian of Gaussian (texture disruption) ───────────
        log = cv2.Laplacian(cv2.GaussianBlur(gray, (3, 3), 0), cv2.CV_64F)
        log_abs = np.uint8(np.clip(np.abs(log), 0, 255))
        _, edges_c = cv2.threshold(log_abs, 30, 255, cv2.THRESH_BINARY)

        # ── Combine all three masks ────────────────────────────────────────
        combined = cv2.bitwise_or(edges_a, thresh_b)
        combined = cv2.bitwise_or(combined, edges_c)

        # morphology: close small gaps, then thin
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        combined = cv2.dilate(combined, kernel, iterations=2)
        combined = cv2.erode(combined, kernel, iterations=1)

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
            # (cracks have long perimeters relative to their filled area)
            perimeter = cv2.arcLength(cnt, True)
            compactness = (perimeter * perimeter) / (area + 1e-5)

            is_elongated = aspect >= min_aspect
            is_crack_like = compactness > 50   # long thin shape

            if is_elongated or is_crack_like:
                # colour by method — yellow contour + magenta bounding rect
                cv2.drawContours(overlay, [cnt], -1, CRACK_COLOR, 2)
                cv2.rectangle(overlay, (x, y), (x + w, y + h), HIGHLIGHT_COLOR, 1)
                label = f"crack {area:.0f}px"
                cv2.putText(overlay, label, (x, y - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, CRACK_COLOR, 1)
                crack_count += 1

        return overlay, crack_count > 0, crack_count
