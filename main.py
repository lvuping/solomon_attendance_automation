import argparse
import json
from requests_hawk import HawkAuth
import requests
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

load_dotenv()
USER_ID = os.getenv('USER_ID')
API_KEY = os.getenv('API_KEY')
TIMEZONE_NAME = os.getenv('TIMEZONE_NAME')

START_HOUR_IN_MORNING = 7
END_HOUR = 17

# TIMEZONE = '+0100' # 시차가 있을 때 1 사용


def get_start_of_work(target_date):
    random_minute = random.randint(45, 57)
    target_date = target_date.replace(hour=START_HOUR_IN_MORNING, minute=random_minute, second=0, microsecond=0)
    return target_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def get_end_of_work(target_date):
    random_minute = random.randint(1, 59)
    target_date = target_date.replace(hour=END_HOUR, minute=random_minute, second=0, microsecond=0)
    return target_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def do_attendance(target_date):
    payload = {
        'userId': USER_ID,
        'start': get_start_of_work(target_date),
        'end': get_end_of_work(target_date),
        'timezoneName': TIMEZONE_NAME,
        # 'end': None, #you set None, You need to finish manually
        # 'timezone': TIMEZONE,
        'type': 'work'
    }

    url = 'https://app.absence.io/api/v2/timespans/create'
    data = json.dumps(payload)
    hawk_auth = HawkAuth(id=USER_ID, key=API_KEY, server_url=url)

    request_response = requests.post(url, auth=hawk_auth, data=data, headers={'Content-Type': 'application/json'})

    return request_response


def main():
    current_date = datetime.utcnow()
    days_ago = args.days_ago  # Get the number of days ago from the argument

    start_date = current_date - timedelta(days=days_ago)

    for i in range(days_ago + 1):
        target_date = start_date + timedelta(days=i)

        # Skip weekends and today
        if target_date.weekday() >= 5 or target_date.date() == current_date.date():
            continue

        response = do_attendance(target_date)
        if response is not False and response.ok:
            print(f'Done: {target_date}')
        else:
            print('Error: ' + response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--days_ago', type=int, help='Number of days ago to start from', default=5)
    args = parser.parse_args()
    main()
