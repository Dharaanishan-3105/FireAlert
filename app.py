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
        # Live camera via browser (works on cloud, phone, and computer)
        st.subheader("Live camera detection")
        st.caption("Uses **your device camera** in the browser — works on phone and computer. Click **START** below and allow camera access.")
        try:
            import av
            from streamlit_webrtc import webrtc_streamer

            def video_frame_callback(frame):
                img = frame.to_ndarray(format="bgr24")
                fire_detected, annotated = run_detection(img, detector)
                if fire_detected and email_config:
                    if (time.time() - getattr(detector, "last_email_time", 0)) >= detector.email_cooldown:
                        detector.email_sender = email_config["sender"]
                        detector.email_password = email_config["password"]
                        detector.email_recipient = email_config["recipient"]
                        detector.send_email_alert(annotated)
                return av.VideoFrame.from_ndarray(annotated, format="bgr24")

            webrtc_streamer(
                key="fire-live",
                video_frame_callback=video_frame_callback,
                media_stream_constraints={"video": True, "audio": False},
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            )
            st.caption("Detection results appear on the video (boxes and **Fire Detected!**). Use the alarm in the sidebar for sound.")
        except ImportError:
            st.info("**Live camera** uses your browser’s camera (works on phone and computer). Install: `pip install streamlit-webrtc av` then restart.")
            st.code("pip install streamlit-webrtc av", language="bash")

if __name__ == "__main__":
    main()
