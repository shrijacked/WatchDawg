import os

LOG_FILE = "logs/events.log"
WEEKLY_SUMMARY = "logs/weekly_summary.txt"


def generate_report():
    if not os.path.exists(LOG_FILE):
        print("No logs found.")
        return

    print("Daily Activity Report:")
    with open(LOG_FILE, "r") as log_file:
        for line in log_file:
            print(line.strip())


def generate_weekly_report():
    if not os.path.exists(LOG_FILE):
        print("No logs found.")
        return

    with open(LOG_FILE, "r") as log_file, open(WEEKLY_SUMMARY, "w") as summary_file:
        for line in log_file:
            summary_file.write(line)

    print(f"Weekly report saved to {WEEKLY_SUMMARY}")
    return WEEKLY_SUMMARY


if __name__ == "__main__":
    generate_report()
