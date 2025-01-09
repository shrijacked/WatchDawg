import os
import json
from datetime import datetime

LOG_FILE = "../logs/events.log"

def generate_report():
    if not os.path.exists(LOG_FILE):
        print("No logs found.")
        return

    print("Daily Activity Report:")
    with open(LOG_FILE, "r") as log_file:
        for line in log_file:
            print(line.strip())

if __name__ == "__main__":
    generate_report()
