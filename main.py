import argparse
import json
from requests_hawk import HawkAuth
import requests
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

load_dotenv()
USER_ID1 = os.getenv("USER_ID1")
API_KEY1 = os.getenv("API_KEY1")

USER_ID2 = os.getenv("USER_ID2")
API_KEY2 = os.getenv("API_KEY2")

TIMEZONE_NAME = os.getenv("TIMEZONE_NAME")

START_HOUR_IN_MORNING = 7
END_HOUR = 17

# TIMEZONE = '+0100' # 시차가 있을 때 1 사용


def get_start_of_work(target_date):
    random_minute = random.randint(45, 57)
    target_date = target_date.replace(
        hour=START_HOUR_IN_MORNING, minute=random_minute, second=0, microsecond=0
    )
    return target_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_end_of_work(target_date):
    random_minute = random.randint(1, 59)
    target_date = target_date.replace(
        hour=END_HOUR, minute=random_minute, second=0, microsecond=0
    )
    return target_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def do_attendance(target_date, api_key, user_id):
    payload = {
        "userId": user_id,
        "start": get_start_of_work(target_date),
        "end": get_end_of_work(target_date),
        "timezoneName": TIMEZONE_NAME,
        "type": "work",
    }

    url = "https://app.absence.io/api/v2/timespans/create"
    data = json.dumps(payload)
    hawk_auth = HawkAuth(id=user_id, key=api_key, server_url=url)

    request_response = requests.post(
        url, auth=hawk_auth, data=data, headers={"Content-Type": "application/json"}
    )

    return request_response


def main():
    current_date = datetime.utcnow()
    days_ago = args.days_ago  # Get the number of days ago from the argument

    start_date = current_date - timedelta(days=days_ago)

    for i in range(days_ago + 1):
        target_date = start_date + timedelta(days=i)

        if target_date.date() == current_date.date():  # Check if target_date is today
            continue  # Skip processing today

        if target_date.weekday() < 5:  # Check if it's a weekday
            response1 = do_attendance(target_date, API_KEY1, USER_ID1)
            response2 = do_attendance(target_date, API_KEY2, USER_ID2)
            if (
                response1 is not False
                and response1.ok
                and response2 is not False
                and response2.ok
            ):
                print(f"Done: {target_date}")
            else:
                print("Error: " + response1.text)
                print("Error: " + response2.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--days_ago", type=int, help="Number of days ago to start from", default=30
    )
    args = parser.parse_args()
    main()
