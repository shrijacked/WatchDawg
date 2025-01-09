import cv2
import torch
import time
import os
import logging
from datetime import datetime
import numpy as np
from send_mail import send_email  # Import the email functionality

THRESHOLD_SECONDS = 10  # Time threshold for trespass detection
MODEL_PATH = "../weights/yolov5s.pt"  # Path to YOLOv5 weights
LOG_DIR = "../logs/"  # Directory for logs
DUMMY_FRAMES = 5

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "events.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def setup_logging(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def load_model(model_path):
    return torch.hub.load("ultralytics/yolov5", "custom", path=model_path, force_reload=True)


def send_mac_notification(message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"Security Alert\"'")


def update_heatmap(frame, heatmap):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if heatmap is None:
        heatmap = np.zeros_like(gray, dtype=np.float32)
    heatmap += cv2.GaussianBlur(gray, (15, 15), 0)
    return heatmap


def display_heatmap(heatmap):
    if heatmap is not None:
        normalized_heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(normalized_heatmap.astype(np.uint8), cv2.COLORMAP_JET)
        cv2.imshow("Heatmap", heatmap_color)


def detect_person(video_source, model, threshold_seconds=THRESHOLD_SECONDS, log_dir=LOG_DIR):
    cap = cv2.VideoCapture(video_source)
    person_detected_time = None
    buzzer_triggered = False
    heatmap = None

    for _ in range(DUMMY_FRAMES):
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

        # Run YOLO inference
        results = model(frame)
        detected_objects = results.pandas().xyxy[0]

        for _, row in detected_objects.iterrows():
            # Draw bounding boxes for all detections
            xmin, ymin, xmax, ymax, label, confidence = int(row["xmin"]), int(row["ymin"]), int(row["xmax"]), int(row["ymax"]), row["name"], row["confidence"]
            if label == "person":
                logger.info(f"""
                Xmin: {xmin}
                Ymin: {ymin}
                
                Xmax: {xmax}
                Ymax: {ymax}
                
                X: {x}
                Y: {y}
                h: {h}
                w: {w}           
                """)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            if label == "person" and xmin >= x and ymin >= y and xmax <= x + w and ymax <= y + h:
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                current_time = time.time()
                if not person_detected_time or (current_time - person_detected_time < 2):
                    person_detected_time = current_time

                elapsed_time = current_time - person_detected_time
                logger.info(f"Person detected for {elapsed_time:.2f} seconds.")
                if elapsed_time >= threshold_seconds and not buzzer_triggered:
                    logger.info("[ALERT] Trespasser detected!")
                    send_mac_notification("Trespasser detected in restricted area!")
                    send_email(
                        subject="Security Alert: Trespasser Detected",
                        body=f"A trespasser was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
                        attachment=None,
                    )
                    buzzer_triggered = True
                    break
        else:
            # Reset if no person is detected
            person_detected_time = None
            buzzer_triggered = False

        # Update and display heatmap
        heatmap = update_heatmap(frame, heatmap)
        display_heatmap(heatmap)

        # Show the detection frame
        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    setup_logging(LOG_DIR)
    model = load_model(MODEL_PATH)
    detect_person(0, model, THRESHOLD_SECONDS, LOG_DIR)  # Use webcam as the video source


if __name__ == "__main__":
    main()
