import cv2
import os
from datetime import datetime


def setup_directories(data_dir="data/"):
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_video_writer(data_dir, fourcc, fps=20.0, frame_size=(640, 480)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(data_dir, f"processed_{timestamp}.avi")
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
    return out, video_path


def record_video():
    """Records video from webcam."""
    data_dir = setup_directories()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Unable to access the webcam.")
        return

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out, video_path = get_video_writer(data_dir, fourcc)

    print(f"Recording video to {video_path}... Press 'q' to stop.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to capture video frame. Exiting...")
                break

            out.write(frame)
            cv2.imshow("Live Video", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\n[INFO] Video capture stopped by user.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Video capture interrupted. Cleaning up resources...")

    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"[INFO] Video saved to {video_path}")


def process_uploaded_video(video_path):
    """Reads and processes an uploaded video file."""
    if not os.path.exists(video_path):
        print("[ERROR] File not found. Please provide a valid path.")
        return

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("[ERROR] Unable to open video source:", video_path)
        return

    data_dir = setup_directories()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_size = (
        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    )

    out, processed_path = get_video_writer(data_dir, fourcc, fps, frame_size)

    print(f"Processing video: {video_path}... Press 'q' to stop.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[INFO] End of video reached.")
                break

            out.write(frame)
            cv2.imshow("Uploaded Video", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\n[INFO] Video processing stopped by user.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Video processing interrupted. Cleaning up resources...")

    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"[INFO] Processed video saved to {processed_path}")


if __name__ == "__main__":
    choice = input("Enter 'live' for webcam recording or provide video file path: ").strip()

    if choice.lower() == "live":
        record_video()
    elif os.path.exists(choice):
        process_uploaded_video(choice)
    else:
        print("[ERROR] Invalid input. Please enter 'live' or a valid video file path.")

