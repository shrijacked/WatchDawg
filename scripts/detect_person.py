import cv2
import torch
import time
import os
from datetime import datetime
import numpy as np

# Paths and constants
THRESHOLD_SECONDS = 10
MODEL_PATH = "../weights/yolov5s.pt"
LOG_DIR = "../logs/"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Heatmap variables
heatmap = None

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, force_reload=True)

def log_event(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file_path = os.path.join(LOG_DIR, "events.log")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{timestamp} - {event}\n")

def send_mac_notification(message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"Security Alert\"'")

def update_heatmap(frame):
    global heatmap
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if heatmap is None:
        heatmap = np.zeros_like(gray, dtype=np.float32)
    heatmap += cv2.GaussianBlur(gray, (15, 15), 0)

def display_heatmap():
    global heatmap
    if heatmap is not None:
        normalized_heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(normalized_heatmap.astype(np.uint8), cv2.COLORMAP_JET)
        cv2.imshow("Heatmap", heatmap_color)

def detect_person(video_source):
    cap = cv2.VideoCapture(video_source)
    person_detected_time = None
    buzzer_triggered = False

    # ROI selection
    ret, frame = cap.read()
    if ret:
        roi = cv2.selectROI("Select ROI", frame, False, False)
        x, y, w, h = map(int, roi)
        cv2.destroyWindow("Select ROI")
    else:
        print("Failed to capture frame for ROI selection.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference
        results = model(frame)
        detected_objects = results.pandas().xyxy[0]

        # Check for persons in the ROI
        for _, row in detected_objects.iterrows():
            if row['name'] == 'person':
                xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                if xmin >= x and ymin >= y and xmax <= x + w and ymax <= y + h:
                    if not person_detected_time:
                        person_detected_time = time.time()

                    elapsed_time = time.time() - person_detected_time
                    if elapsed_time >= THRESHOLD_SECONDS and not buzzer_triggered:
                        print("[ALERT] Trespasser detected!")
                        send_mac_notification("Trespasser detected in restricted area!")
                        log_event("Trespasser detected in restricted area!")
                        buzzer_triggered = True

                break
        else:
            person_detected_time = None
            buzzer_triggered = False

        # Update and display heatmap
        update_heatmap(frame)
        display_heatmap()

        # Show detection frame
        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_person(0)  # Use webcam
