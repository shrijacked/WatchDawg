import cv2
import torch
import time
import os
import logging
from datetime import datetime
import numpy as np
from utils.send_mail import send_email


THRESHOLD_SECONDS = 10
MODEL_PATH = "weights/yolov5s.pt"
LOG_DIR = "logs/"
ALERT_SOUND_PATH = "sounds/alert.wav"
MAX_ALLOWED_PEOPLE = 5

# Logging setup
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "events.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def load_model(model_path):
    return torch.hub.load("ultralytics/yolov5", "custom", path=model_path, force_reload=True)


def play_alert():
    if os.path.exists(ALERT_SOUND_PATH):
        os.system(f"afplay {ALERT_SOUND_PATH}")  # Replace with suitable command for your OS


def detect_person(video_source, model, threshold_seconds=THRESHOLD_SECONDS):
    cap = cv2.VideoCapture(video_source)
    person_detected_time = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        detected_objects = results.pandas().xyxy[0]

        people_count = 0
        for _, row in detected_objects.iterrows():
            if row["name"] == "person":
                people_count += 1
                xmin, ymin, xmax, ymax = map(int, [row["xmin"], row["ymin"], row["xmax"], row["ymax"]])
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)

        if people_count > MAX_ALLOWED_PEOPLE:
            logger.warning(f"Crowd alert! {people_count} people detected.")
            play_alert()
            send_email(
                subject="Crowd Alert",
                body=f"More than {MAX_ALLOWED_PEOPLE} people detected at {datetime.now()}",
            )

        cv2.imshow("Person Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    model = load_model(MODEL_PATH)
    detect_person(0, model)


if __name__ == "__main__":
    main()
