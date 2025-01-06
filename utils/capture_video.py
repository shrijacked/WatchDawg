import cv2
import os
from datetime import datetime

def setup_directories(data_dir="../data/"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def get_video_writer(data_dir, fourcc, fps=20.0, frame_size=(640, 480)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(data_dir, f"recording_{timestamp}.avi")
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
    return out, video_path

def capture_video():
    # Setup directories
    data_dir = setup_directories()

    # Video capture settings
    cap = cv2.VideoCapture(0)  # Use the first camera
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Get video writer
    out, video_path = get_video_writer(data_dir, fourcc)

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

if __name__ == "__main__":
    capture_video()
