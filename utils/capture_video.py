import cv2
import os
from datetime import datetime


def setup_directories(data_dir="data/"):
    os.makedirs(data_dir, exist_ok=True)  # Simplified directory creation
    return data_dir


def get_video_writer(data_dir, fourcc, fps=20.0, frame_size=(640, 480)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(data_dir, f"recording_{timestamp}.avi")
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
    return out, video_path


def capture_video():
    data_dir = setup_directories()
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out, video_path = get_video_writer(data_dir, fourcc)

    print(f"Recording video to {video_path}... Press 'q' to stop.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture video frame. Exiting...")
                break

            out.write(frame)
            cv2.imshow("Video Capture", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):  # Stop on 'q' key press
                print("\nVideo capture stopped by user.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Video capture interrupted. Cleaning up resources...")

    finally:
        if cap.isOpened():
            cap.release()
        if out is not None:
            out.release()
        cv2.destroyAllWindows()
        print(f"[INFO] Video saved to {video_path}")


if __name__ == "__main__":
    try:
        capture_video()
    except KeyboardInterrupt:
        print("\n[INFO] Program terminated by user.")
