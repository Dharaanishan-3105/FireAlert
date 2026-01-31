# Fire Detection and Alert System

This system uses computer vision and deep learning to detect fire in real-time from a camera feed, trigger an audible alarm, and send email notifications.

## Features

- Real-time fire detection using deep learning
- Audible alarm system
- Email notifications
- Logging of detection events
- Configurable detection threshold

## Setup Instructions

1. Install Python 3.8 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure email settings in `.env` file:
   ```
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_RECIPIENT=recipient@email.com
   ```
4. Place your trained model in the `models` directory
5. Run the system:
   ```bash
   python fire_detection.py
   ```

## System Requirements

- Webcam or IP camera
- Python 3.8+
- Internet connection for email notifications
- Speakers for alarm system

## Configuration

- Adjust detection threshold in `config.py`
- Modify email settings in `.env`
- Configure camera settings in `config.py`

## Safety Notice

This system is designed as an additional safety measure and should not be relied upon as the sole fire detection system. Always maintain proper fire safety equipment and protocols. 