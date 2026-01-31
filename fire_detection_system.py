import cv2
import numpy as np
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
try:
    from playsound import playsound
except ImportError:
    # playsound often fails on Linux/cloud (no desktop audio). Alarm still works:
    # - Streamlit app: uses st.audio() so the browser plays the alert.
    # - Local run: install with pip install playsound for system alarm.
    playsound = None
import time
import os
import threading

class FireDetectionSystem:
    def __init__(self, use_camera=True):
        # Initialize YOLO model
        print("Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')
        
        # Optional: initialize camera (skip for Streamlit image/upload mode)
        self.cap = None
        if use_camera:
            print("Initializing camera...")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("Failed to open camera")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Detection settings
        self.detection_threshold = 0.3
        self.consecutive_detections = 0
        self.consecutive_threshold = 1  # Lowered for instant response
        self.last_email_time = 0
        self.email_cooldown = 30  # Reduced to 30 seconds
        
        # Email settings
        self.email_sender = "your_email@gmail.com"
        self.email_password = "your_app_password"
        self.email_recipient = "recipient@email.com"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Alarm sound
        self.alarm_sound = "assets/alarm.mp3"
        if not os.path.exists(self.alarm_sound):
            print(f"Warning: Alarm sound not found at {self.alarm_sound}")
        
        # Initialize alarm thread
        self.alarm_thread = None
        self.is_alarm_playing = False
        
        # Initialize background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=16, detectShadows=False)
        
        # Previous frame for motion detection
        self.prev_frame = None
        
        # Expanded fire color ranges (including bright white/yellow)
        self.fire_ranges = [
            {'lower': np.array([0, 30, 180]), 'upper': np.array([15, 255, 255])},   # Red/Orange
            {'lower': np.array([16, 50, 180]), 'upper': np.array([35, 255, 255])}, # Yellow
            {'lower': np.array([0, 0, 200]), 'upper': np.array([180, 80, 255])}    # Bright white/yellow
        ]
    
    def detect_fire(self, frame):
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Create fire mask
        fire_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for color_range in self.fire_ranges:
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            fire_mask = cv2.bitwise_or(fire_mask, mask)
        # Morphological operations
        kernel = np.ones((3,3), np.uint8)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel)
        # Detect motion
        if self.prev_frame is not None:
            frame_diff = cv2.absdiff(frame, self.prev_frame)
            frame_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
            _, motion_mask = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            combined_mask = cv2.bitwise_and(fire_mask, motion_mask)
        else:
            combined_mask = fire_mask
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        color_motion_fire = False
        annotated_frame = frame.copy()
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:  # Lower threshold so smaller flames are detected
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h if h > 0 else 0
                if 0.15 < aspect_ratio < 1.5:  # Slightly wider range for flame shapes
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 165, 255), 2)
                    cv2.putText(annotated_frame, "Fire (Color+Motion)", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
                    color_motion_fire = True
        # YOLO detection (exclude person/human to avoid false fire on people)
        yolo_fire = False
        COCO_PERSON_CLASS_ID = 0
        yolo_results = self.model(frame, conf=self.detection_threshold, verbose=False, device='cpu', imgsz=256)
        for result in yolo_results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id == COCO_PERSON_CLASS_ID:
                    continue  # Never treat person as fire (avoids false alarm on phone/self)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cropped_mask = fire_mask[y1:y2, x1:x2]
                if np.sum(cropped_mask) > 0:
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(annotated_frame, f"Fire: {conf:.2f}", (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    yolo_fire = True
        # Trigger fire if color+motion suggests fire OR YOLO (non-person) box has fire color
        # (YOLO COCO has no "fire" class, so requiring both missed real fire; either signal is enough)
        fire_detected = color_motion_fire or yolo_fire
        status = "Fire Detected!" if fire_detected else "No Fire"
        color = (0, 0, 255) if fire_detected else (0, 255, 0)
        cv2.putText(annotated_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, color, 2)
        self.prev_frame = frame.copy()
        return fire_detected, annotated_frame
    
    def play_alarm(self):
        """Play alarm sound in a separate thread (desktop/CLI). Alert is always available in Streamlit via st.audio()."""
        if playsound is None:
            return  # Use Streamlit app's st.audio() or install playsound for local run
        if not self.is_alarm_playing:
            self.is_alarm_playing = True
            try:
                playsound(self.alarm_sound)
            except Exception as e:
                print(f"Failed to play alarm: {str(e)}")
            finally:
                self.is_alarm_playing = False
    
    def send_email_alert(self, frame_to_attach):
        current_time = time.time()
        if current_time - self.last_email_time < self.email_cooldown:
            return
        
        image_path = "fire_detected_image.jpg"
        cv2.imwrite(image_path, frame_to_attach)

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.email_recipient
            msg['Subject'] = "Fire Detection Alert - Image Attached"
            body = "Fire has been detected in the monitored area. Please check the attached image for details!"
            msg.attach(MIMEText(body, 'plain'))

            # Attach image
            with open(image_path, 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                msg.attach(img)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            try:
                server.login(self.email_sender, self.email_password)
            except smtplib.SMTPAuthenticationError:
                print("Email authentication failed. Please check your credentials.")
                print("Make sure you're using an App Password if 2FA is enabled.")
                return
            
            server.send_message(msg)
            server.quit()
            
            self.last_email_time = current_time
            print("Email alert sent successfully with image attached!")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Check if your Gmail account has 2FA enabled")
            print("2. Generate an App Password from your Google Account settings")
            print("3. Update the email_password in the script with the App Password")
        finally:
            # Clean up the image file
            if os.path.exists(image_path):
                os.remove(image_path)
    
    def run(self):
        print("Starting fire detection system...")
        print("Press 'q' to quit")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Detect fire
                fire_detected, annotated_frame = self.detect_fire(frame)
                
                # Update consecutive detections
                if fire_detected:
                    self.consecutive_detections += 1
                    if self.consecutive_detections >= self.consecutive_threshold:
                        print("Fire detected!")
                        # Play alarm in separate thread
                        if not self.is_alarm_playing:
                            self.alarm_thread = threading.Thread(target=self.play_alarm)
                            self.alarm_thread.start()
                        # Send email
                        self.send_email_alert(annotated_frame)
                else:
                    self.consecutive_detections = 0
                
                # Display frame
                cv2.imshow('Fire Detection', annotated_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print("\nStopping fire detection system...")
        finally:
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            print("System stopped")

if __name__ == "__main__":
    try:
        system = FireDetectionSystem()
        system.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if your camera is working")
        print("2. Verify your email settings")
        print("3. Ensure the alarm sound file exists") 