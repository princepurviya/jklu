"""
app.py — Streamlit dashboard for Structural Damage Detection.

Run with:  streamlit run app.py
"""

import cv2
import time
import numpy as np
import streamlit as st
from PIL import Image
from datetime import datetime

from detector import DamageDetector
from comparator import compare_images, detect_misplaced_objects
from utils import trigger_alert, save_baseline, load_baseline, clear_baseline


def resize_to_width(image: np.ndarray, target_width: int) -> np.ndarray:
    """Resize image preserving aspect ratio; skip if already smaller."""
    h, w = image.shape[:2]
    if w <= target_width:
        return image
    scale = target_width / float(w)
    new_h = max(1, int(h * scale))
    return cv2.resize(image, (target_width, new_h), interpolation=cv2.INTER_AREA)


def push_alert_once(message: str, severity: str = "HIGH", detections: list | None = None):
    """Avoid alert flooding by suppressing immediate duplicates."""
    if st.session_state.alerts and st.session_state.alerts[0]["message"] == message:
        return
    st.session_state.alerts.insert(0, trigger_alert(message, detections=detections, severity=severity))


def grab_fresh_frame(video_source, camera_source: str, warmup_reads: int = 3):
    """Open camera source and return the freshest available frame."""
    cap = cv2.VideoCapture(video_source)
    if camera_source == "IP Webcam":
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        return None

    grabbed = None
    for _ in range(max(1, warmup_reads)):
        ok, frame = cap.read()
        if ok:
            grabbed = frame
    cap.release()
    return grabbed

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI-Powered Exhibit Monitoring System",
    page_icon=None,
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* header bar */
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2rem;
        letter-spacing: 1px;
    }
    .main-header p {
        color: #b0b0d0;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }

    /* metric cards */
    .metric-card {
        background: #1e1e2f;
        border: 1px solid #3a3a5c;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .metric-card h3 {
        color: #a78bfa; margin: 0; font-size: 0.85rem; text-transform: uppercase;
    }
    .metric-card .value {
        color: #ffffff; font-size: 1.8rem; font-weight: 700;
    }

    /* alert box */
    .alert-box {
        background: #2d1b1b;
        border-left: 4px solid #ef4444;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
        color: #fca5a5;
        font-size: 0.88rem;
    }
    .alert-box .ts {
        color: #888; font-size: 0.75rem;
    }

    /* safe status */
    .safe-box {
        background: #1b2d1b;
        border-left: 4px solid #22c55e;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        color: #86efac;
        font-size: 0.9rem;
        margin-bottom: 0.6rem;
    }

    /* hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {display:none;}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>AI-Powered Exhibit Monitoring System</h1>
    <p>Real-time detection of wall cracks, pillar damage &amp; unwanted objects</p>
</div>
""", unsafe_allow_html=True)

# ── Session state defaults ──────────────────────────────────────────────────
if "detector" not in st.session_state:
    st.session_state.detector = DamageDetector()
if "baseline" not in st.session_state:
    saved = load_baseline()
    st.session_state.baseline = saved  # may be None
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False
if "frame_counter" not in st.session_state:
    st.session_state.frame_counter = 0
if "capture_baseline_requested" not in st.session_state:
    st.session_state.capture_baseline_requested = False
if "last_frame" not in st.session_state:
    st.session_state.last_frame = None
if "baseline_captured_at" not in st.session_state:
    st.session_state.baseline_captured_at = None

detector: DamageDetector = st.session_state.detector

# ── Sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    st.subheader("📷 Camera Source")
    camera_source = st.radio("Select Camera Source", ["Laptop Webcam", "IP Webcam"])
    
    if camera_source == "Laptop Webcam":
        cam_index = st.number_input("Camera index", 0, 10, 0, key="cam_idx")
        video_source = int(cam_index)
    else:
        ip_url = st.text_input("IP Webcam URL", value="http://192.168.1.5:8080/video", key="ip_url")
        video_source = ip_url

    st.subheader("🎯 Detection Settings")
    confidence = st.slider("YOLO confidence", 0.1, 1.0, 0.40, 0.05)
    detector.confidence = confidence

    crack_sensitivity = st.select_slider(
        "Crack detection sensitivity",
        options=["low", "medium", "high"],
        value="high",
        help="Higher = more sensitive (may show more false positives)",
    )

    ssim_threshold = st.slider("SSIM alert threshold", 0.50, 1.0, 0.85, 0.05)

    st.subheader("⚡ Performance")
    processing_width = st.slider("Processing width (px)", 320, 1280, 640, 80)
    yolo_every_n = st.slider("Run YOLO every N frames", 1, 6, 2)
    crack_every_n = st.slider("Run crack detection every N frames", 1, 6, 2)
    ssim_every_n = st.slider("Run SSIM every N frames", 1, 6, 3)
    target_fps = st.slider("Target display FPS", 5, 30, 12)

    st.subheader("🖼️ Baseline Image")
    uploaded = st.file_uploader("Upload baseline image", type=["png", "jpg", "jpeg"])
    if uploaded:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.session_state.baseline = img
        save_baseline(img)
        st.session_state.baseline_captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success("✅ Baseline uploaded!")

    if st.button("📸 Capture Baseline from Camera", key="capture_sidebar"):
        captured = grab_fresh_frame(video_source, camera_source)
        if captured is None:
            st.error(f"❌ Could not capture baseline from source: {video_source}")
        else:
            st.session_state.baseline = captured.copy()
            st.session_state.last_frame = captured.copy()
            save_baseline(captured)
            st.session_state.baseline_captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("✅ Baseline captured successfully from camera.")

    if st.session_state.baseline is not None:
        st.image(
            cv2.cvtColor(st.session_state.baseline, cv2.COLOR_BGR2RGB),
            caption="Current Baseline", use_container_width=True,
        )
        if st.session_state.baseline_captured_at:
            st.caption(f"Captured at: {st.session_state.baseline_captured_at}")

    if st.button("🗑️ Clear Alerts"):
        st.session_state.alerts = []

    if st.button("❌ Remove Baseline"):
        st.session_state.baseline = None
        st.session_state.baseline_captured_at = None
        clear_baseline()
        st.success("🗑️ Baseline removed!")
        st.rerun()

# ── Tabs ────────────────────────────────────────────────────────────────────
tab_camera, tab_upload, tab_compare = st.tabs([
    "📹 Real-Time Camera", "📤 Upload Image", "🔍 Before / After Comparison"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Real-time camera
# ════════════════════════════════════════════════════════════════════════════
with tab_camera:
    col_feed, col_alerts = st.columns([3, 1])

    with col_feed:
        st.subheader("Live Camera Feed")
        start_btn = st.button("▶️ Start Camera", key="start_cam")
        stop_btn = st.button("⏹️ Stop Camera", key="stop_cam")
        capture_bl = st.button("📸 Capture as Baseline", key="capture_bl")
        frame_placeholder = st.empty()
        status_placeholder = st.empty()

    with col_alerts:
        st.subheader("🚨 Alerts")
        alert_placeholder = st.empty()
        metric_obj = st.empty()
        metric_crack = st.empty()
        metric_ssim = st.empty()
        metric_fps = st.empty()

    if stop_btn:
        st.session_state.camera_running = False

    if capture_bl:
        st.session_state.capture_baseline_requested = True

    if st.session_state.capture_baseline_requested and st.session_state.last_frame is not None and not st.session_state.camera_running:
        st.session_state.baseline = st.session_state.last_frame.copy()
        save_baseline(st.session_state.baseline)
        st.session_state.baseline_captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.capture_baseline_requested = False
        st.success("✅ Baseline captured from latest frame.")

    if start_btn:
        st.session_state.camera_running = True
        
        if camera_source == "IP Webcam" and not video_source:
             st.error("❌ Please enter a valid IP Webcam URL.")
             st.session_state.camera_running = False
        else:
             cap = cv2.VideoCapture(video_source)
             if camera_source == "IP Webcam":
                 cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
             if not cap.isOpened():
                 st.error(f"❌ Cannot open camera at source: {video_source}")
                 st.session_state.camera_running = False
             else:
                 status_placeholder.info(f"🟢 Camera ({camera_source}) is running — press **Stop Camera** to end.")
                 last_detections = []
                 last_crack_found = False
                 last_crack_count = 0
                 last_ssim_score = None
                 last_misplaced_count = 0

                 while st.session_state.camera_running:
                     frame_start = time.perf_counter()
                     st.session_state.frame_counter += 1
                     frame_id = st.session_state.frame_counter

                     ret, frame = cap.read()
                     if not ret:
                         st.warning("⚠️ Failed to read frame.")
                         break

                     st.session_state.last_frame = frame.copy()

                     frame_proc = resize_to_width(frame, processing_width)
                     annotated = frame_proc.copy()

                     # — YOLO detection (throttled)
                     if frame_id % yolo_every_n == 0:
                         annotated, last_detections = detector.detect_objects(frame_proc)
                     detections = last_detections

                     # — Crack detection (throttled)
                     if frame_id % crack_every_n == 0:
                         annotated, last_crack_found, last_crack_count = detector.detect_cracks(
                             annotated,
                             sensitivity=crack_sensitivity,
                         )
                     crack_found = last_crack_found
                     crack_count = last_crack_count

                     # — Baseline comparison + misplaced detection (throttled)
                     if st.session_state.baseline is not None and frame_id % ssim_every_n == 0:
                         baseline_proc = resize_to_width(st.session_state.baseline, processing_width)
                         result = compare_images(baseline_proc, frame_proc, ssim_threshold)
                         last_ssim_score = result["ssim_score"]

                         diff_img = result["diff_image"]
                         annotated, last_misplaced_count = detect_misplaced_objects(diff_img, annotated, min_area=5000)

                     ssim_score = last_ssim_score
                     misplaced_count = last_misplaced_count
     
                     # — Alerts
                     if detections:
                         labels = ", ".join(d["label"] for d in detections)
                         push_alert_once(f"Unwanted objects detected: {labels}", detections=detections)
     
                     if crack_found:
                         push_alert_once(f"Possible structural cracks detected ({crack_count} regions)")
     
                     if ssim_score is not None and ssim_score < ssim_threshold:
                         push_alert_once(
                             f"Scene changed — SSIM {ssim_score:.2%} (threshold {ssim_threshold:.0%})",
                             severity="MEDIUM",
                         )
                         
                     if misplaced_count > 0:
                         push_alert_once(
                             f"MISPLACED OBJECT DETECTED ({misplaced_count} large regions)",
                             severity="HIGH",
                         )
     
                     # keep only last 50 alerts
                     st.session_state.alerts = st.session_state.alerts[:50]
     
                     # — Render frame
                     frame_placeholder.image(
                         cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                         channels="RGB", use_container_width=True,
                     )
     
                     # — Render metrics
                     metric_obj.markdown(
                         f'<div class="metric-card"><h3>Objects</h3>'
                         f'<div class="value">{len(detections)}</div></div>',
                         unsafe_allow_html=True,
                     )
                     metric_crack.markdown(
                         f'<div class="metric-card"><h3>Cracks</h3>'
                         f'<div class="value">{crack_count if crack_found else 0}</div></div>',
                         unsafe_allow_html=True,
                     )
                     ssim_display = f"{ssim_score:.2%}" if ssim_score is not None else "N/A"
                     metric_ssim.markdown(
                         f'<div class="metric-card"><h3>SSIM</h3>'
                         f'<div class="value">{ssim_display}</div></div>',
                         unsafe_allow_html=True,
                     )
                     elapsed = max(1e-6, time.perf_counter() - frame_start)
                     fps_now = 1.0 / elapsed
                     metric_fps.markdown(
                         f'<div class="metric-card"><h3>Loop FPS</h3>'
                         f'<div class="value">{fps_now:.1f}</div></div>',
                         unsafe_allow_html=True,
                     )
     
                     # — Render alerts
                     alert_html = ""
                     for a in st.session_state.alerts[:10]:
                         alert_html += (
                             f'<div class="alert-box">'
                             f'<span class="ts">{a["timestamp"]}</span><br>{a["message"]}'
                             f'</div>'
                         )
                     if not st.session_state.alerts:
                         alert_html = '<div class="safe-box">✅ No damage detected</div>'
                     alert_placeholder.markdown(alert_html, unsafe_allow_html=True)
     
                     # — Capture baseline on button press
                     if st.session_state.capture_baseline_requested:
                         st.session_state.baseline = frame.copy()
                         save_baseline(frame)
                         st.session_state.baseline_captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                         st.session_state.capture_baseline_requested = False
                         status_placeholder.success("✅ Baseline captured successfully.")
     
                     target_interval = 1.0 / float(target_fps)
                     wait_for = max(0.0, target_interval - (time.perf_counter() - frame_start))
                     if wait_for > 0:
                         time.sleep(wait_for)
     
                 cap.release()
                 status_placeholder.info("⏹️ Camera stopped.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Upload Image for detection
# ════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.subheader("Upload an Image for Detection")
    uploaded_img = st.file_uploader("Choose an image…", type=["png", "jpg", "jpeg"],
                                    key="upload_detect")
    if uploaded_img:
        file_bytes = np.asarray(bytearray(uploaded_img.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        col_orig, col_det = st.columns(2)
        with col_orig:
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                     caption="Original Image", use_container_width=True)

        # YOLO detection
        annotated, detections = detector.detect_objects(img)
        # Crack detection
        annotated, crack_found, crack_count = detector.detect_cracks(annotated, sensitivity=crack_sensitivity)

        with col_det:
            st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                     caption="Detection Results", use_container_width=True)

        # Results summary
        if detections or crack_found:
            st.error("🚨 **Damage / Anomaly Detected!**")
            if detections:
                st.write("**Unwanted Objects:**")
                for d in detections:
                    st.write(f"- **{d['label']}** — confidence {d['confidence']:.0%}")
            if crack_found:
                st.write(f"**Possible Cracks:** {crack_count} region(s) detected")
        else:
            st.success("✅ No damage or unwanted objects detected.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Before / After Comparison
# ════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.subheader("Before / After Comparison")

    col_before, col_after = st.columns(2)

    with col_before:
        st.write("**Baseline (Before)**")
        baseline_up = st.file_uploader("Upload baseline", type=["png", "jpg", "jpeg"],
                                        key="bl_upload")
        if baseline_up:
            file_bytes = np.asarray(bytearray(baseline_up.read()), dtype=np.uint8)
            baseline_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        elif st.session_state.baseline is not None:
            baseline_img = st.session_state.baseline
        else:
            baseline_img = None

        if baseline_img is not None:
            st.image(cv2.cvtColor(baseline_img, cv2.COLOR_BGR2RGB),
                     caption="Baseline", use_container_width=True)
            if st.session_state.baseline_captured_at and baseline_up is None:
                st.caption(f"Using captured baseline from: {st.session_state.baseline_captured_at}")
        else:
            st.info("Upload or capture a baseline image first.")

    with col_after:
        st.write("**Current (After)**")
        current_up = st.file_uploader("Upload current image", type=["png", "jpg", "jpeg"],
                                       key="curr_upload")
        if current_up:
            file_bytes = np.asarray(bytearray(current_up.read()), dtype=np.uint8)
            current_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            st.image(cv2.cvtColor(current_img, cv2.COLOR_BGR2RGB),
                     caption="Current", use_container_width=True)
        else:
            current_img = None
            st.info("Upload a current image to compare.")

    if baseline_img is not None and current_img is not None:
        st.markdown("---")
        result = compare_images(baseline_img, current_img, ssim_threshold)

        col_diff, col_metrics = st.columns([3, 1])

        with col_diff:
            st.image(cv2.cvtColor(result["diff_image"], cv2.COLOR_BGR2RGB),
                     caption="Difference Heatmap", use_container_width=True)

        with col_metrics:
            score = result["ssim_score"]
            st.markdown(
                f'<div class="metric-card"><h3>SSIM Score</h3>'
                f'<div class="value">{score:.2%}</div></div>',
                unsafe_allow_html=True,
            )
            if result["damage_detected"]:
                st.error(f"🚨 Significant change detected! SSIM {score:.2%} < {ssim_threshold:.0%}")
                alert = trigger_alert(
                    f"Comparison alert — SSIM {score:.2%}",
                    severity="HIGH",
                )
                st.session_state.alerts.insert(0, alert)
            else:
                st.success(f"✅ Scene looks stable. SSIM {score:.2%}")

        # also run YOLO on current image
        st.markdown("---")
        st.subheader("YOLO & Misplacement Detection on Current Image")
        annotated, detections = detector.detect_objects(current_img)
        annotated, crack_found, crack_count = detector.detect_cracks(annotated, sensitivity=crack_sensitivity)
        
        # — Misplaced Object Detection
        annotated, misplaced_count = detect_misplaced_objects(result["diff_image"], annotated, min_area=5000)

        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                 caption="Detection Overlay", use_container_width=True)

        if detections:
            for d in detections:
                st.write(f"- **{d['label']}** — {d['confidence']:.0%}")
        if crack_found:
            st.write(f"- **Cracks:** {crack_count} region(s)")
        if misplaced_count > 0:
            st.error(f"🚨 **Misplaced Objects:** {misplaced_count} large region(s) detected via SSIM (>5000px)")
            
        if not detections and not crack_found and misplaced_count == 0:
            st.success("✅ No anomalies or misplaced objects detected in current image.")
