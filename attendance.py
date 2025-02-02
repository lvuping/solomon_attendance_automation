import json
from requests_hawk import HawkAuth
import requests
from datetime import datetime, timedelta, timezone
import random
from dotenv import load_dotenv
import os

load_dotenv()
USER_ID = os.getenv("USER_ID")
API_KEY = os.getenv("API_KEY")
TIMEZONE_NAME = os.getenv("TIMEZONE_NAME")

START_HOUR = 8
END_HOUR = 17


def get_random_time(date, hour):
    random_minute = random.randint(50, 59)
    # 로컬 시간으로 설정
    local_time = date.replace(hour=hour, minute=random_minute, second=0, microsecond=0)
    utc_time = local_time.astimezone(timezone.utc)

    print(f"생성된 시간 - 로컬(CET): {local_time}, UTC: {utc_time}")

    return utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def record_attendance(date):
    print("\n=== 출퇴근 시간 생성 ===")
    start_time = get_random_time(date, START_HOUR)
    end_time = get_random_time(date, END_HOUR)

    payload = {
        "userId": USER_ID,
        "timezoneName": TIMEZONE_NAME,
        "type": "work",
        "start": start_time,
        "end": end_time,
        "created": end_time,  # 생성 시간 추가
    }

    print(f"\n=== API 요청 정보 ===")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    url = "https://app.absence.io/api/v2/timespans/create"
    hawk_auth = HawkAuth(id=USER_ID, key=API_KEY, server_url=url)

    try:
        response = requests.post(
            url,
            auth=hawk_auth,
            json=payload,  # data=json.dumps(payload) 대신 json 파라미터 사용
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",  # Accept 헤더 추가
            },
        )

        if response.status_code == 201:  # Created
            print(f"출퇴근 기록 완료:")
            print(f"출근 시간: {start_time}")
            print(f"퇴근 시간: {end_time}")
            print("API Response:", response.json())
        else:
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"API 요청 실패: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        print(f"Request payload: {payload}")


def is_weekday(date):
    """주어진 날짜가 평일인지 확인 (0 = 월요일, 6 = 일요일)"""
    return date.weekday() < 5


def main():
    # CET(UTC+1) 기준으로 현재 날짜 설정
    cet_tz = timezone(timedelta(hours=1))
    current_date = datetime.now(cet_tz)

    print(f"\n=== 디버깅 정보 ===")
    print(f"현재 시간 (CET): {current_date}")
    print(f"현재 시간 (UTC): {current_date.astimezone(timezone.utc)}")
    print("==================\n")

    # 과거 3일치 기록 생성
    days_processed = 0
    days_back = 0

    while days_processed < 3:
        # days_back일 전의 날짜 계산
        past_date = current_date - timedelta(days=days_back)
        days_back += 1

        print(f"\n--- 처리할 날짜 정보 ---")
        print(f"대상 날짜 (CET): {past_date}")
        print(f"대상 날짜 (UTC): {past_date.astimezone(timezone.utc)}")

        # 주말이면 건너뛰기
        if not is_weekday(past_date):
            print(f"{past_date.date()}는 주말이므로 건너뜁니다.")
            continue

        print(f"\n{past_date.date()} 기록 생성 중...")
        record_attendance(past_date)
        days_processed += 1


if __name__ == "__main__":
    main()
