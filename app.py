"""
Fire Detection System - Streamlit App (real-time only)
Run with: streamlit run app.py
"""
import streamlit as st
import cv2
import numpy as np
import time
import os
from datetime import timedelta

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
    st.markdown("**Real-time** fire detection from your device camera. Works on phone and computer.")

    alarm_path = "assets/alarm.mp3"

    # Sidebar
    with st.sidebar:
        st.header("Settings")
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
        st.subheader("🔊 Alarm")
        if os.path.exists(alarm_path):
            st.audio(alarm_path, format="audio/mp3")
            st.caption("Plays automatically when fire is detected on camera.")

    detector = get_fire_detector()
    detector.detection_threshold = detection_threshold

    # Live camera only (real-time)
    st.subheader("Live camera detection")
    st.caption("Uses **your device camera** — works on phone and computer. Click **START** below and allow camera access.")

    try:
        import av
        from streamlit_webrtc import webrtc_streamer

        # Shared file so worker callback can signal "fire detected" to main app (alarm plays automatically)
        _trigger_file = os.environ.get("FIRE_ALERT_TRIGGER_FILE", "/tmp/fire_alert_detected.txt")

        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            fire_detected, annotated = run_detection(img, detector)
            if fire_detected:
                try:
                    with open(_trigger_file, "w") as f:
                        f.write(str(time.time()))
                except Exception:
                    pass
                if email_config:
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

        # Poll trigger file and play alarm automatically when fire was detected (callback runs in worker)
        @st.fragment(run_every=timedelta(seconds=1))
        def fire_alert_auto():
            try:
                if os.path.exists(_trigger_file):
                    with open(_trigger_file, "r") as f:
                        t = float(f.read().strip() or 0)
                    if t and (time.time() - t) < 10:
                        st.error("🚨 **Fire detected!** — Alarm playing.")
                        if os.path.exists(alarm_path):
                            st.audio(alarm_path, format="audio/mp3", autoplay=True, key="fire_alarm_auto")
                        return
            except Exception:
                pass
            if os.path.exists(alarm_path):
                st.caption("Alarm will play automatically when fire is detected on the video.")

        fire_alert_auto()

    except ImportError:
        st.info("Install: `pip install streamlit-webrtc av` then restart.")
        st.code("pip install streamlit-webrtc av", language="bash")

if __name__ == "__main__":
    main()
