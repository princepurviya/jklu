# 🖼️ AI-Powered Exhibit Monitoring System

An automated, real-time monitoring system designed to detect **structural damage** (cracks, pillar issues), **misplaced exhibits**, and **unwanted objects** (garbage, bags, etc.) in galleries or infrastructure environments.

Built with **Python**, **Streamlit**, **OpenCV**, and **YOLOv8**.

---

## 🚀 Key Features

### 1. 🔍 Structural Damage Detection
Detects wall cracks and surface anomalies using an advanced image processing pipeline:
- **Multi-Method Heuristics:** Combines CLAHE (Contrast Enhancement), Canny Edge Detection, and Laplacian of Gaussian (Texture Disruption).
- **Adjustable Sensitivity:** Low, Medium, and High sensitivity modes accessible via the sidebar to tune detection for different lighting and surfaces.

### 2. 🔀 Misplaced Object Detection (SSIM)
Detects shifted exhibits or newly introduced large items using **Structural Similarity Index (SSIM)**:
- **Baseline Comparison:** Compares live frames against a saved "Normal" baseline image.
- **Large Object Filtering:** Automatically ignores small noise or cables and focuses only on large misplaced objects (>5000px area).
- **Bounding Boxes:** Highlights moved objects with red boxes and labels them as **"MISPLACED OBJECT"**.

### 3. 🛡️ Unwanted Object Detection (YOLOv8)
Integrates a pretrained **YOLOv8n** deep learning model to identify common unwanted items:
- Detects bottles, bags, backpacks, phones, and other items that shouldn't be in the gallery space.
- Real-time overlay of bounding boxes and confidence scores.

### 4. 📷 Multi-Source Camera Support
Flexibility in monitoring hardware:
- **Laptop Webcam:** Standard hardware support (Index 0, 1, etc.).
- **IP Webcam:** Connect your mobile phone or network camera via URL (e.g., `http://192.168.1.5:8080/video`).
- **Start/Stop Controls:** Manually control when the monitoring starts to save resources.

### 5. 📊 Interactive Streamlit Dashboard
A premium-looking dark-themed UI that provides:
- **Live Feed Tab:** Real-time video with all detection overlays.
- **Results Metrics:** Instant counters for Objects, Cracks, and Similarity Scores.
- **Alert Panel:** A persistent notification log for all detected anomalies.
- **Before/After Analysis:** Side-by-side comparison of baseline vs. current frames with difference heatmaps.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/princepurviya/jklu.git
   cd Road-Damage-Detection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 📖 How to Use

1. **Set the Baseline:** Start the camera and click **"Capture as Baseline"** or upload a reference image of the exhibit in its perfect state.
2. **Configure Sensitivity:** Use the sidebar sliders to adjust the YOLO confidence and crack detection sensitivity.
3. **Monitor Alerts:** Keep an eye on the **Alerts** panel. If someone moves an exhibit or leaves a bag behind, the system will highlight the region and log the timestamp.
4. **IP Webcam:** To use your phone as a camera, install an "IP Webcam" app, copy the URL provided by the app, and paste it into the **IP Webcam URL** field in the sidebar.

---

## 🔧 Technical Stack

- **Frontend:** Streamlit (Custom CSS for Premium UI)
- **Computer Vision:** OpenCV, Scikit-Image (SSIM)
- **Deep Learning:** Ultralytics YOLOv8 (v8n)
- **Languages:** Python 3.x
