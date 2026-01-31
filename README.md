# Fire Detection and Alert System

This system uses computer vision and deep learning to detect fire in real-time from a camera feed, trigger an audible alarm, and send email notifications.

## Features

- Real-time fire detection using deep learning
- Audible alarm system
- Email notifications
- Logging of detection events
- Configurable detection threshold

## why FireAlert?

This project aims to enhance safety through automated fire monitoring. The core features include:

🧠🟣 Deep Learning Detection:
 Utilizes YOLOv8 for accurate, real-time fire identification.

🔔🟢 Multi-Channel Alerts:
 Triggers alarms, emails, and logs events to ensure rapid response.

⚙️🟠 Modular Architecture:
 Integrates visual analysis, notifications, and configuration management seamlessly.

💾🟡 Easy Setup:
 Defines dependencies like OpenCV, NumPy, and Ultralytics for reliable deployment.

🚨🟤 Rapid Response:
 Combines multiple detection methods to minimize false positives and maximize safety.


## Setup Instructions

1. Install Python 3.8 or higher

2. Installation

   **Clone the repository**
   ```bash
   git clone <https://github.com/Dharaanishan-3105/FireAlert>
   cd FireAlert
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure email settings in `.env` file:
   ```
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_RECIPIENT=recipient@email.com
   ```
5. Place your trained model in the `models` directory
6. Run the system:
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