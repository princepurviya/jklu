# AI-Powered Exhibit Monitoring System

Real-time monitoring platform for galleries/museums to detect:
- structural damage (cracks / scene changes),
- misplaced exhibits (object position shift),
- foreign or unwanted objects.

This repository contains a **full-stack setup**:
- React + Vite frontend (`frontend/`)
- Node.js + Express backend (`backend/`)
- Streamlit + OpenCV + YOLO dashboard (`app.py`)

---

## System Architecture

Frontend (React)
→ Backend API (Express)
→ AI Dashboard (Streamlit)
→ Camera feeds + CV pipeline

Detection flow in dashboard:
1. Preprocess frames (grayscale + Gaussian blur) for robust comparison.
2. Damage branch: abs-diff/SSIM style scene change + contour area filtering.
3. Object branch: YOLO detections for moved/foreign/unwanted objects.
4. Alert engine logs timestamped events.

---

## Key Features

- **Damage Detection**
   - Noise-robust preprocessing.
   - Threshold + contour-area filtering to suppress false alerts.
- **Misplacement Detection**
   - Position-based object shift from baseline detections.
- **Foreign/Unwanted Object Detection**
   - YOLOv8n-based object detection with filtered alert classes.
- **Baseline Workflow**
   - Baseline captured using `frame.copy()`.
   - Frame-stabilization skip after baseline capture.
- **Camera Support**
   - Laptop webcam and IP webcam URLs.
- **Multi-Camera Control (dashboard sidebar)**
   - Add/manage camera sources and run feeds.

---

## Project Structure

```text
jklu/
├── app.py                  # Streamlit AI dashboard
├── detector.py             # YOLO + crack/object utilities
├── comparator.py           # frame comparison + contour filtering
├── utils.py
├── backend/                # Express API
│   ├── server.js
│   └── routes/
│       ├── health.js
│       ├── system.js
│       └── contact.js
└── frontend/               # React + Vite UI
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB running locally (default backend config)

---

## Setup

### 1) Python dependencies (dashboard)

```bash
pip install -r requirements.txt
```

### 2) Backend dependencies

```bash
cd backend
npm install
cd ..
```

### 3) Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Run (3 terminals)

### Terminal A — Backend

```bash
cd backend
npm run dev
```

Backend runs on: `http://localhost:5000`

### Terminal B — Frontend

```bash
cd frontend
npx vite --host 0.0.0.0 --port 5173
```

Frontend runs on: `http://localhost:5173`

### Terminal C — Streamlit Dashboard

```bash
python -m streamlit run app.py --server.headless true --server.port 8501
```

Dashboard runs on: `http://localhost:8501`

---

## API Endpoints (Backend)

- `GET /api/health`
- `GET /api/health/db`
- `POST /api/contact`
- `POST /api/system/start` (starts Streamlit process and returns `dashboardUrl`)

---

## How to Use

1. Start all services.
2. Open frontend: `http://localhost:5173`.
3. Click **Start System** (opens dashboard in same tab).
4. In dashboard sidebar:
    - select/add camera,
    - capture baseline,
    - configure thresholds,
    - start monitoring.

---

## Recommended Default Tuning

- Gaussian blur: `21x21`
- Diff threshold: `40`
- Min changed area: `2000` (adjust per scene)
- Movement threshold: `~50 px`
- Skip frames after baseline capture: `5`

---

## Troubleshooting

- **Sidebar/settings panel not visible**
   - Make sure Streamlit toolbar/header is not hidden by custom CSS.
   - Hard refresh browser (`Ctrl + F5`).
- **Port already in use**
   - Free ports `5000`, `5173`, `8501` or run on alternate ports.
- **Frontend loads but API fails**
   - Check backend is running and `GET /api/health` returns success.
- **Frequent false alerts**
   - Increase min contour area / movement threshold.
   - Re-capture baseline with stable camera.

---

## Tech Stack

- **Frontend:** React, Vite, Framer Motion
- **Backend:** Node.js, Express, MongoDB (Mongoose)
- **AI/CV:** Python, Streamlit, OpenCV, Ultralytics YOLOv8, NumPy, scikit-image
