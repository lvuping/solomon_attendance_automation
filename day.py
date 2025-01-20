import argparse
import json
from requests_hawk import HawkAuth
import requests
from datetime import datetime, timedelta, timezone
import random
from dotenv import load_dotenv
import os

load_dotenv()
USER_ID1 = os.getenv("USER_ID1")
API_KEY1 = os.getenv("API_KEY1")

TIMEZONE_NAME = os.getenv("TIMEZONE_NAME")

START_HOUR_IN_MORNING = 8
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


def do_attendance_start(target_date, api_key, user_id):
    # 이미 출근 기록이 있는지 확인
    if os.path.exists("date_log.txt"):
        print("이미 출근 기록이 존재합니다.")
        return None

    payload = {
        "userId": user_id,
        "timezoneName": TIMEZONE_NAME,
        "type": "work",
        "start": get_start_of_work(target_date),
        "end": None,
    }

    url = "https://app.absence.io/api/v2/timespans/create"
    data = json.dumps(payload)
    hawk_auth = HawkAuth(id=user_id, key=api_key, server_url=url)

    response = requests.post(
        url, auth=hawk_auth, data=data, headers={"Content-Type": "application/json"}
    )

    if response.ok:
        print("API Response:", response.json())
        timespan_data = response.json()
        timespan_id = timespan_data.get("_id")

        with open("date_log.txt", "w") as f:
            f.write(f"{timespan_id}\n")
            f.write(f"{get_start_of_work(target_date)}\n")
    else:
        print("Error Response:", response.text)

    return response


def do_attendance_end(target_date, api_key, user_id):
    try:
        # 저장된 timespan 정보 읽기
        with open("date_log.txt", "r") as f:
            lines = f.readlines()
            timespan_id = lines[0].strip()  # 첫 번째 줄에서 ID 읽기
            start_time = lines[1].strip()  # 두 번째 줄에서 시작 시간 읽기

        payload = {
            "start": start_time,
            "end": get_end_of_work(target_date),
            "type": "work",
            "timezoneName": TIMEZONE_NAME,
        }

        url = f"https://app.absence.io/api/v2/timespans/{timespan_id}"
        data = json.dumps(payload)
        hawk_auth = HawkAuth(id=user_id, key=api_key, server_url=url)

        response = requests.put(
            url, auth=hawk_auth, data=data, headers={"Content-Type": "application/json"}
        )

        if response.ok:
            # 성공적으로 업데이트되면 로그 파일 삭제
            os.remove("date_log.txt")
            print("API Response:", response.json())
            print("퇴근 처리가 완료되어 date_log.txt 파일을 삭제했습니다.")
        else:
            print("Error Response:", response.text)

        return response
    except FileNotFoundError:
        print("출근 기록을 찾을 수 없습니다. (date_log.txt 파일이 없습니다)")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="테스트용 날짜 (YYYY-MM-DD 형식)", default=None)
    parser.add_argument("--hour", help="테스트용 시간 (0-23)", type=int, default=None)
    args = parser.parse_args()

    if args.date:
        # 테스트용 날짜 사용
        current_date = datetime.strptime(args.date, "%Y-%m-%d")
        if args.hour is not None:
            current_date = current_date.replace(hour=args.hour)
    else:
        # 현지 시간 사용 (UTC+1)
        current_date = datetime.now(timezone(timedelta(hours=1)))

    current_hour = current_date.hour
    print(f"현재 시간: {current_date}")

    # 오전 출근 기록
    if current_hour < END_HOUR:
        print(f"출근 기록 시작: {current_date}")
        response1 = do_attendance_start(current_date, API_KEY1, USER_ID1)
        if response1 and response1.ok:
            print(f"출근 기록 완료: {current_date}")
        elif response1:
            print("출근 기록 오류: " + str(current_date) + ": " + response1.text)
        else:
            print("이미 출근 처리가 되어있습니다.")

    # 오후 퇴근 기록
    if current_hour >= END_HOUR:
        print(f"퇴근 기록 시작: {current_date}")
        response1 = do_attendance_end(current_date, API_KEY1, USER_ID1)
        if response1 and response1.ok:
            print(f"퇴근 기록 완료: {current_date}")
        else:
            print(
                "퇴근 기록 오류: "
                + str(current_date)
                + ": "
                + (response1.text if response1 else "출근 기록이 없습니다")
            )


if __name__ == "__main__":
    main()
