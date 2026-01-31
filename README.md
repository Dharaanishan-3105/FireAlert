<h1 align="center">
  <span style="font-size: 3.5em; font-weight: 800; letter-spacing: -2px;">🔥 FireAlert</span>
</h1>

<p align="center">
  <strong style="font-size: 1.2em;">Real-time fire detection using computer vision and deep learning</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-00d4aa?style=flat-square" alt="YOLOv8" />
  <img src="https://img.shields.io/badge/OpenCV-4.8-5c3ee8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Streamlit-Web_App-e6522c?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Why FireAlert?](#-why-firealert)
- [Setup](#-setup-instructions)
- [Running the App](#-running-the-app)
- [System Requirements](#-system-requirements)
- [Configuration](#-configuration)
- [Safety Notice](#-safety-notice)

---

## 🎯 Overview

FireAlert uses **computer vision** and **deep learning** to detect fire in real time from a camera feed. It can trigger an audible alarm, send email notifications, and log detection events—helping you respond faster and stay safer.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| **Real-time detection** | Deep learning–based fire identification from live video |
| **Audible alarm** | Built-in alarm sound when fire is detected |
| **Email alerts** | Optional email notifications with attached snapshot |
| **Event logging** | Detection events logged for review |
| **Configurable threshold** | Tune detection sensitivity to your environment |
| **Streamlit web app** | Browser UI: upload images, camera snapshot, or live webcam |

---

## 💡 Why FireAlert?

This project aims to **enhance safety through automated fire monitoring**. Core capabilities:

| | Capability |
|---|------------|
| 🧠 **Deep learning** | Uses **YOLOv8** for accurate, real-time fire identification. |
| 🔔 **Multi-channel alerts** | Triggers alarms, emails, and logs events for rapid response. |
| ⚙️ **Modular design** | Integrates visual analysis, notifications, and config cleanly. |
| 💾 **Easy setup** | Clear dependencies (OpenCV, NumPy, Ultralytics) for reliable deployment. |
| 🚨 **Rapid response** | Combines multiple detection methods to reduce false positives and improve safety. |

---

## 🛠 Setup Instructions

### 1. Prerequisites

- **Python 3.8 or higher**

### 2. Clone the repository

```bash
git clone https://github.com/Dharaanishan-3105/FireAlert
cd FireAlert
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Email configuration (optional)

Create a `.env` file for email alerts:

```env
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@email.com
```

> Use a Gmail **App Password** if you have 2FA enabled.

### 5. Model and assets

- Place your trained model in the `models` directory (or use the default YOLO weights).
- Ensure `assets/alarm.mp3` exists for the alarm sound.

---

## 🚀 Running the App

### Option A — Streamlit (web UI)

```bash
streamlit run app.py
```

Then open the URL in your browser. You can:

- **Analyze image** — Upload a photo or take a camera snapshot.
- **Live camera** — Run detection from your webcam for a set duration.

### Option B — Command-line (desktop)

```bash
python fire_detection_system.py
```

Press **`q`** to quit. The system uses your default webcam.

---

## 📦 System Requirements

- Webcam or IP camera
- Python 3.8+
- Internet connection (for email notifications)
- Speakers (for alarm)

---

## ⚙️ Configuration

| What | Where |
|------|--------|
| Detection threshold | `fire_detection_system.py` or Streamlit sidebar |
| Email settings | `.env` or Streamlit sidebar |
| Camera settings | `fire_detection_system.py` (or config if you add one) |

---

## ⚠️ Safety Notice

> **This system is an *additional* safety measure** and should **not** replace proper fire safety equipment or protocols. Always maintain smoke detectors, extinguishers, and evacuation plans as required by your location.

---

<p align="center">
  <sub>Built with 🔥 for safety</sub>
</p>
