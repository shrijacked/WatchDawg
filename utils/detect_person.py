import cv2
import torch
import time
import os
import logging
from datetime import datetime
import numpy as np
from send_mail import send_email  # Import email functionality

THRESHOLD_SECONDS = 10
MODEL_PATH = "../weights/yolov5s.pt"
LOG_DIR = "../logs/"
ALERT_SOUND_PATH = "../sounds/alert.wav"  # Optional alert sound

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "events.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

def load_model(model_path):
    return torch.hub.load("ultralytics/yolov5", "custom", path=model_path, force_reload=True)

def send_alerts(message):
    # Send Email
    send_email(
        subject="Security Alert: Trespasser Detected",
        body=message,
    )

    # Optional: Play alert sound
    if os.path.exists(ALERT_SOUND_PATH):
        os.system(f"afplay {ALERT_SOUND_PATH}")  # For macOS
        # Use 'playsound' module for cross-platform support

def detect_person(video_source, model, threshold_seconds=THRESHOLD_SECONDS):
    cap = cv2.VideoCapture(video_source)
    person_detected_time = None

    # Allow the user to set ROI
    ret, frame = cap.read()
    if ret:
        roi = cv2.selectROI("Select ROI", frame, False, False)
        x, y, w, h = map(int, roi)
        cv2.destroyWindow("Select ROI")
    else:
        logger.error("Failed to capture frame for ROI selection.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        detected_objects = results.pandas().xyxy[0]

        for _, row in detected_objects.iterrows():
            xmin, ymin, xmax, ymax, label, confidence = int(row["xmin"]), int(row["ymin"]), int(row["xmax"]), int(row["ymax"]), row["name"], row["confidence"]
            if label == "person" and xmin >= x and ymin >= y and xmax <= x + w and ymax <= y + h:
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                current_time = time.time()
                if not person_detected_time:
                    person_detected_time = current_time

                elapsed_time = current_time - person_detected_time
                if elapsed_time >= threshold_seconds:
                    logger.info("[ALERT] Trespasser detected!")
                    send_alerts(f"Trespasser detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    break

        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    model = load_model(MODEL_PATH)
    detect_person(0, model, THRESHOLD_SECONDS)  # Use webcam as the video source

if __name__ == "__main__":
    main()
