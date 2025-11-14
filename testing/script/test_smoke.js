import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

export const errorRate = new Rate("errors");

const BASE = __ENV.BASE || "http://localhost:8000";
const RATE = __ENV.RATE || 10;
const DURATION = __ENV.DURATION || 60;
const PRE_VU = __ENV.PRE_VU || 5;
const MAX_VU = __ENV.MAX_VU || 15;

const DEVICE_ID = __ENV.DEVICE_ID || "11111111-1111-1111-1111-111111111111";

export let options = {
  thresholds: {
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],
  },

  scenarios: {
    smoke: {
      executor: "constant-arrival-rate",
      rate: RATE,
      timeUnit: "1s",
      duration: `${DURATION}s`,
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
    },
  },
};

export default function () {
  // url: home
  let home_resp = http.get(`${BASE}`, {
    tags: { endpoint: "home" },
  });
  check(home_resp, {
    "home 200": (r) => r.status === 200,
    "home response time": (r) => r.timings.duration < 800,
  }) || errorRate.add(1);

  // url: health check
  let health_check_resp = http.get(`${BASE}/health`, {
    tags: { endpoint: "health_check" },
  });
  check(health_check_resp, {
    "health_check 200": (r) => r.status === 200,
    "health_check response time": (r) => r.timings.duration < 800,
  }) || errorRate.add(1);

  // url: list devices
  let list_device_resp = http.get(`${BASE}/devices`, {
    tags: { endpoint: "list_device" },
  });
  check(list_device_resp, {
    "list_device 200": (r) => r.status === 200,
    "list_device response time": (r) => r.timings.duration < 800,
    "list_device json array": (r) => {
      try {
        return Array.isArray(r.json());
      } catch (e) {
        return false;
      }
    },
  }) || errorRate.add(1);

  // Url: get specific device
  if (DEVICE_ID) {
    let device_resp = http.get(`${BASE}/devices/${DEVICE_ID}`, {
      tags: { endpoint: "get_device" },
    });
    check(device_resp, {
      "get_device 200 or 404": (r) => r.status === 200 || r.status === 404,
      "get_device response time": (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);
  }

  //   sleep(1);
}

export function handleSummary(data) {
  return {
    "summary.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
