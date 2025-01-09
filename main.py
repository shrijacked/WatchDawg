import os
import argparse
from utils.capture_video import capture_video
from utils.detect_person import main as detect_person_main
from utils.generate_report import generate_report, generate_weekly_report


def setup_environment():
    # Ensure required directories exist
    required_dirs = ["data", "logs", "weights", "sounds"]
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)


def main():
    setup_environment()

    parser = argparse.ArgumentParser(description="Security System Application")
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["capture", "detect", "daily_report", "weekly_report"],
        help=(
            "Action to perform:\n"
            "capture: Record a video\n"
            "detect: Run person detection\n"
            "daily_report: Generate daily activity report\n"
            "weekly_report: Generate weekly summary report"
        ),
    )
    args = parser.parse_args()

    if args.action == "capture":
        print("Starting video capture...")
        capture_video()
    elif args.action == "detect":
        print("Starting person detection...")
        detect_person_main()
    elif args.action == "daily_report":
        print("Generating daily report...")
        generate_report()
    elif args.action == "weekly_report":
        print("Generating weekly summary...")
        weekly_report = generate_weekly_report()
        print(f"Weekly summary saved to {weekly_report}")
    else:
        print("Invalid action. Use --help for guidance.")


if __name__ == "__main__":
    main()
