import cv2
import time
import torch
from datetime import datetime
import os

# Load YOLO model (PyTorch or ONNX)
MODEL_PATH = "../weights/yolov5s.pt"
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)

# Configurations
THRESHOLD_SECONDS = 10  # Alert if person is detected for this duration
LOG_DIR = "../logs/"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def detect_person(video_path):
    cap = cv2.VideoCapture(video_path)
    person_detected_time = None
    buzzer_triggered = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference
        results = model(frame)

        # Check if any person is detected
        detected_objects = results.pandas().xyxy[0]  # Extract detections
        if 'person' in detected_objects['name'].values:
            if not person_detected_time:
                person_detected_time = time.time()

            elapsed_time = time.time() - person_detected_time
            if elapsed_time >= THRESHOLD_SECONDS and not buzzer_triggered:
                print(f"[ALERT] Person detected for {elapsed_time} seconds.")
                buzzer_triggered = True
                trigger_buzzer()
                log_event()

        else:
            person_detected_time = None
            buzzer_triggered = False

        # Display the frame (optional)
        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def trigger_buzzer():
    print("[BUZZER] Activating alarm...")

def log_event():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "events.log"), "a") as log_file:
        log_file.write(f"{timestamp} - Person detected for {THRESHOLD_SECONDS} seconds\n")

# Test the function with a sample video
detect_person("../data/sample_video.avi")
