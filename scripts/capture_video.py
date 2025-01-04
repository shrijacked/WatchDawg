import cv2
import os
from datetime import datetime

# Setup directories
DATA_DIR = "../data/"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Video capture settings
cap = cv2.VideoCapture(0)  # Use the first camera
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# Filename for the video file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
video_path = os.path.join(DATA_DIR, f"recording_{timestamp}.avi")
out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

print(f"Recording video to {video_path}... Press 'q' to stop.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Write the frame to the video file
    out.write(frame)

    # Display the frame (optional)
    cv2.imshow("Video Capture", frame)

    # Break the loop on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video saved to {video_path}")
