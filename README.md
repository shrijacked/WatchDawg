# WatchDawg

WatchDawg is a security surveillance system that uses computer vision to detect trespassers and send alerts. It leverages YOLOv5 for person detection and can send email notifications when a trespasser is detected.

## Features

- **Real-time person detection** using YOLOv5
- **Heatmap generation** for activity visualization
- **Email notifications** for security alerts
- **Video recording** and saving

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shrijacked/WatchDawg.git
cd WatchDawg
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install the Required Packages
```bash
pip install -r requirements.txt
```

## Configuration

- **Email Credentials**: Update the email credentials in `send_mail.py` with your own email and password.
- **Model Path**: Modify the `MODEL_PATH` in `detect_person.py` if needed.
- **Log Directory**: Adjust the `LOG_DIR` in `detect_person.py` if necessary.

## Usage

### Capture Video
To capture video from your webcam and save it to the `data` directory, run:
```bash
python utils/capture_video.py
```

### Detect Person
To start the person detection system, run:
```bash
python utils/detect_person.py
```

### Generate Report
To generate a daily activity report from the logs, use:
```bash
python utils/generate_report.py
```

### Send Email
To test the email functionality, run:
```bash
python utils/send_mail.py
```

## License
This project is licensed under the MIT License.
```

