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


def do_attendance(target_date, api_key, user_id, is_end=False):
    # 기본 payload 구성
    payload = {
        "userId": user_id,
        "timezoneName": TIMEZONE_NAME,
        "type": "work",
    }

    # 출퇴근 여부에 따라 시간 필드 추가
    if is_end:
        payload["end"] = get_end_of_work(target_date)
    else:
        payload["start"] = get_start_of_work(target_date)

    url = "https://app.absence.io/api/v2/timespans/create"
    data = json.dumps(payload)
    hawk_auth = HawkAuth(id=user_id, key=api_key, server_url=url)

    request_response = requests.post(
        url, auth=hawk_auth, data=data, headers={"Content-Type": "application/json"}
    )

    return request_response


def main():
    current_date = datetime.utcnow()

    if current_date.weekday() < 5:  # 평일인 경우에만 실행
        current_hour = current_date.hour

        # 오전 출근 기록
        if current_hour < END_HOUR:
            response1 = do_attendance(current_date, API_KEY1, USER_ID1, is_end=False)
            if response1.ok:
                print(f"출근 기록 완료: {current_date}")
            else:
                print("출근 기록 오류: " + str(current_date) + ": " + response1.text)

        # 오후 퇴근 기록
        if current_hour >= END_HOUR:
            response1 = do_attendance(current_date, API_KEY1, USER_ID1, is_end=True)
            if response1.ok:
                print(f"퇴근 기록 완료: {current_date}")
            else:
                print("퇴근 기록 오류: " + str(current_date) + ": " + response1.text)


if __name__ == "__main__":
    main()
