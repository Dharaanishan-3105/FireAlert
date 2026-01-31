"""
Fire Detection System - Streamlit App
Run with: streamlit run app.py
"""
import streamlit as st
import cv2
import numpy as np
import time
import os

# Page config
st.set_page_config(
    page_title="Fire Detection",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_fire_detector():
    """Get or create fire detection system (no camera) for this session."""
    if 'detector' not in st.session_state:
        from fire_detection_system import FireDetectionSystem
        st.session_state.detector = FireDetectionSystem(use_camera=False)
    return st.session_state.detector

def run_detection(frame_bgr, detector):
    """Run fire detection on a single frame. Returns (fire_detected, annotated_frame_bgr)."""
    return detector.detect_fire(frame_bgr)

def main():
    st.title("🔥 Fire Detection System")
    st.markdown("Upload an image, capture from camera, or run **live camera** detection.")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        mode = st.radio(
            "Mode",
            ["Analyze image", "Live camera"],
            help="Analyze a single image or run continuous live detection.",
        )
        detection_threshold = st.slider("Detection confidence", 0.1, 0.9, 0.3, 0.05)
        st.divider()
        st.subheader("Email alert (optional)")
        email_enabled = st.checkbox("Send email on fire", value=False)
        if email_enabled:
            email_sender = st.text_input("Sender email", value="your_email@gmail.com")
            email_password = st.text_input("App password", type="password", value="")
            email_recipient = st.text_input("Recipient email", value="recipient@email.com")
            email_config = {
                "sender": email_sender,
                "password": email_password,
                "recipient": email_recipient,
            }
        else:
            email_config = None
        st.divider()
        # Alarm asset
        alarm_path = "assets/alarm.mp3"
        if os.path.exists(alarm_path):
            st.audio(alarm_path, format="audio/mp3")

    # Apply threshold to detector when we use it
    detector = get_fire_detector()
    detector.detection_threshold = detection_threshold

    if mode == "Analyze image":
        st.subheader("Analyze an image")
        col1, col2 = st.columns(2)
        with col1:
            source = st.radio("Source", ["Upload image", "Camera snapshot"])
            img_file = None
            if source == "Upload image":
                img_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
            else:
                img_file = st.camera_input("Take a photo")
        if img_file is not None:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if frame is not None:
                with st.spinner("Running fire detection..."):
                    fire_detected, annotated = run_detection(frame, detector)
                with col2:
                    st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)
                    if fire_detected:
                        st.error("🚨 Fire detected!")
                        if os.path.exists(alarm_path):
                            st.audio(alarm_path, format="audio/mp3")
                        if email_config and st.button("Send email alert"):
                            detector.email_sender = email_config["sender"]
                            detector.email_password = email_config["password"]
                            detector.email_recipient = email_config["recipient"]
                            detector.send_email_alert(annotated)
                            st.success("Email sent.")
                    else:
                        st.success("No fire detected.")
            else:
                st.warning("Could not decode the image.")
        else:
            with col2:
                st.info("Upload an image or take a snapshot to analyze.")

    else:
        # Live camera mode (runs for a set duration; Streamlit can't process Stop during loop)
        st.subheader("Live camera detection")
        run_seconds = st.sidebar.slider("Live run duration (seconds)", 5, 120, 30)
        st.caption(f"Click **Start** to run detection for **{run_seconds}** seconds. Your webcam will be used.")
        start_btn = st.button("Start live detection", type="primary")
        if start_btn:
            st.session_state.run_live = True
        if st.session_state.get('run_live', False):
            place = st.empty()
            status_placeholder = st.empty()
            progress = st.progress(0)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Could not open camera. Check permissions or try another device.")
                st.session_state.run_live = False
            else:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                start_time = time.time()
                fire_count = 0
                try:
                    while (time.time() - start_time) < run_seconds:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        fire_detected, annotated = run_detection(frame, detector)
                        rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                        place.image(rgb, use_container_width=True)
                        elapsed = time.time() - start_time
                        progress.progress(min(1.0, elapsed / run_seconds))
                        if fire_detected:
                            fire_count += 1
                            status_placeholder.error("🚨 Fire detected!")
                            if email_config:
                                detector.email_sender = email_config["sender"]
                                detector.email_password = email_config["password"]
                                detector.email_recipient = email_config["recipient"]
                                detector.send_email_alert(annotated)
                        else:
                            status_placeholder.success("No fire")
                        time.sleep(0.05)
                finally:
                    cap.release()
                    st.session_state.run_live = False
                    progress.progress(1.0)
                st.success(f"Live run finished. Fire alerts: {fire_count}. Click **Start** to run again.")
        else:
            st.info("Click **Start live detection** to use your webcam.")

if __name__ == "__main__":
    main()
