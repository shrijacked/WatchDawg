import cv2
import torch
import time
import os
from datetime import datetime
import numpy as np
from send_mail import send_email  # Import send_email function from send_mail.py

# Constants
THRESHOLD_SECONDS = 10  # Time threshold for alert (in seconds)
MODEL_PATH = "../weights/yolov5s.pt"  # Path to YOLOv5 model
LOG_DIR = "../logs/"  # Directory for logs
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Heatmap variables
heatmap = None

# Load YOLOv5 model
print("[INFO] Loading YOLOv5 model...")
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, force_reload=True)

def log_event(event):
    """Log the event to a file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file_path = os.path.join(LOG_DIR, "events.log")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{timestamp} - {event}\n")

def send_mac_notification(message):
    """Send a macOS notification."""
    os.system(f"osascript -e 'display notification \"{message}\" with title \"Security Alert\"'")

def update_heatmap(frame):
    """Update the heatmap with new frame data."""
    global heatmap
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if heatmap is None:
        heatmap = np.zeros_like(gray, dtype=np.float32)
    heatmap += cv2.GaussianBlur(gray, (15, 15), 0)

def display_heatmap():
    """Display the heatmap in a separate window."""
    global heatmap
    if heatmap is not None:
        normalized_heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(normalized_heatmap.astype(np.uint8), cv2.COLORMAP_JET)
        cv2.imshow("Heatmap", heatmap_color)

def detect_person(video_source):
    """Detect persons in the video feed."""
    cap = cv2.VideoCapture(video_source)
    person_detected_time = None
    buzzer_triggered = False

    # ROI selection
    print("[INFO] Select the Region of Interest (ROI)...")
    ret, frame = cap.read()
    if ret:
        roi = cv2.selectROI("Select ROI", frame, False, False)
        x, y, w, h = map(int, roi)
        cv2.destroyWindow("Select ROI")
        print(f"[INFO] ROI selected: x={x}, y={y}, w={w}, h={h}")
    else:
        print("[ERROR] Failed to capture frame for ROI selection.")
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

                        # Send email notification
                        send_email(
                            subject="Security Alert: Trespasser Detected",
                            body=f"A trespasser was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
                            attachment=None  # Optional: Add a video file path if required
                        )

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
    print("[INFO] Starting person detection...")
    detect_person(0)  # Use webcam (change to a file path for recorded videos)
