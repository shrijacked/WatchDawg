import os
import argparse
from utils.capture_video import capture_video
from utils.detect_person import main as detect_person_main
from utils.generate_report import generate_report

def setup_environment():
    # Ensure required directories exist
    required_dirs = ["../data", "../logs", "../weights", "../sounds"]
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)


def main():
    # Setup the environment
    setup_environment()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Security System")
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["capture", "detect", "report"],
        help="Action to perform: capture (record video), detect (detect intruders), or report (generate daily report)."
    )
    args = parser.parse_args()

    if args.action == "capture":
        print("Starting video capture...")
        capture_video()
    elif args.action == "detect":
        print("Starting person detection...")
        detect_person_main()
    elif args.action == "report":
        print("Generating daily report...")
        generate_report()
    else:
        print("Invalid action. Use --help for guidance.")


if __name__ == "__main__":
    main()
