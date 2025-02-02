import Hawk from "@hapi/hawk";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname } from "path";

// ES 모듈에서 __dirname 사용하기 위한 설정
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 환경변수 로드
dotenv.config();

const USER_ID = process.env.USER_ID;
const API_KEY = process.env.API_KEY;
const TIMEZONE_NAME = process.env.TIMEZONE_NAME;

const START_HOUR = 8;
const END_HOUR = 18;

function getRandomTime(date, hour) {
  // END_HOUR일 때는 0-15분 사이의 랜덤값, 그 외에는 1-59분 사이의 랜덤값
  const randomMinute =
    hour === END_HOUR
      ? Math.floor(Math.random() * 16) // 0-15 사이의 랜덤값
      : Math.floor(Math.random() * 15) + 45; // 45-59 사이의 랜덤값

  // 입력받은 날짜의 복사본 생성
  const localTime = new Date(date);

  // CET 시간대로 시간 설정 (UTC+1)
  localTime.setUTCHours(hour - 1, randomMinute, 0, 0); // CET는 UTC+1이므로 1시간을 빼줍니다

  console.log(
    `생성된 시간 - 로컬(CET): ${new Date(
      localTime.getTime() + 3600000
    )}, UTC: ${localTime}`
  );

  return localTime.toISOString();
}

async function recordAttendance(date) {
  console.log("\n=== 출퇴근 시간 생성 ===");
  const startTime = getRandomTime(date, START_HOUR);
  const endTime = getRandomTime(date, END_HOUR);

  const payload = {
    userId: USER_ID,
    timezoneName: TIMEZONE_NAME,
    type: "work",
    start: startTime,
    end: endTime,
    created: endTime,
  };

  console.log("\n=== API 요청 정보 ===");
  console.log("Payload:", JSON.stringify(payload, null, 2));

  const url = "https://app.absence.io/api/v2/timespans/create";

  // Hawk 인증 헤더 생성
  const credentials = {
    id: USER_ID,
    key: API_KEY,
    algorithm: "sha256",
  };

  const { header: hawkHeader } = Hawk.client.header(url, "POST", {
    credentials,
  });

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: hawkHeader,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("출퇴근 기록 완료:");
      console.log(`출근 시간: ${startTime}`);
      console.log(`퇴근 시간: ${endTime}`);
      console.log("API Response:", data);
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.log("API 요청 실패:", error.message);
    if (error instanceof Response) {
      console.log(`Status code: ${error.status}`);
      const errorBody = await error.text();
      console.log(`Response body: ${errorBody}`);
    }
    console.log("Request payload:", payload);
  }
}

function isWeekday(date) {
  return date.getDay() !== 0 && date.getDay() !== 6;
}

async function main() {
  // 오늘 날짜로 설정
  const specificDate = new Date();
  specificDate.setHours(0, 0, 0, 0); // 오늘 자정으로 시간 설정
  // CET는 UTC+1이므로 한 시간을 더해줍니다
  const cetTime = new Date(specificDate.getTime() + 1 * 60 * 60 * 1000);

  console.log("\n--- 처리할 날짜 정보 ---");
  console.log(`대상 날짜 (CET): ${cetTime}`);
  console.log(`대상 날짜 (UTC): ${specificDate}`);

  if (!isWeekday(cetTime)) {
    console.log(
      `${cetTime.toISOString().split("T")[0]}는 주말이므로 처리하지 않습니다.`
    );
    return;
  }

  console.log(`\n${cetTime.toISOString().split("T")[0]} 기록 생성 중...`);
  await recordAttendance(cetTime);
}

main().catch(console.error);
