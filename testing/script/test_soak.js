import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

export const errorRate = new Rate("errors");

const BASE = __ENV.BASE || "http://localhost:8000";

const RATE_SOAK = Number(__ENV.RATE_SOAK) || 30;
const DURATION_RAMP = __ENV.DURATION_RAMP || "5m"; // warmup
const DURATION_SOAK = __ENV.DURATION_SOAK || "2h"; // long, steady load
const PRE_VU = Number(__ENV.PRE_VU) || 10;
const MAX_VU = Number(__ENV.MAX_VU) || 100;

const DEVICE_ID = __ENV.DEVICE_ID || "11111111-1111-1111-1111-111111111111";

export const options = {
  thresholds: {
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],

    // SLO: Latency
    "http_req_duration{endpoint:home}": ["p(95)<600", "p(99)<1200"],
    "http_req_duration{endpoint:health_check}": ["p(95)<400", "p(99)<800"],
    "http_req_duration{endpoint:list_device}": ["p(95)<1000", "p(99)<2000"],
    "http_req_duration{endpoint:get_device}": ["p(95)<1500", "p(99)<2500"],
  },

  scenarios: {
    soak: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,

      startRate: 1,
      stages: [
        { duration: DURATION_RAMP, target: RATE_SOAK }, // Warm up
        { duration: DURATION_SOAK, target: RATE_SOAK }, // Long, steady load
        { duration: "2m", target: 0 }, // cool-down
      ],
    },
  },

  cloud: {
    name: "Soak Testing",
  },
};

export default function () {
  // url: home
  const home_resp = http.get(`${BASE}`, {
    tags: { endpoint: "home" },
  });
  check(home_resp, {
    "home 200": (r) => r.status === 200,
  }) || errorRate.add(1);

  // url: health check
  const health_check_resp = http.get(`${BASE}/health`, {
    tags: { endpoint: "health_check" },
  });
  check(health_check_resp, {
    "health_check 200": (r) => r.status === 200,
  }) || errorRate.add(1);

  // // url: list devices
  // const list_device_resp = http.get(`${BASE}/devices`, {
  //   tags: { endpoint: "list_device" },
  // });
  // check(list_device_resp, {
  //   "list_device 200": (r) => r.status === 200,
  //   "list_device json array": (r) => {
  //     try {
  //       return Array.isArray(r.json());
  //     } catch (e) {
  //       return false;
  //     }
  //   },
  // }) || errorRate.add(1);

  // // url: get specific device
  // if (DEVICE_ID) {
  //   const device_resp = http.get(`${BASE}/devices/${DEVICE_ID}`, {
  //     tags: { endpoint: "get_device" },
  //   });
  //   check(device_resp, {
  //     "get_device 200 or 404": (r) => r.status === 200 || r.status === 404,
  //   }) || errorRate.add(1);
  // }
}

export function handleSummary(data) {
  return {
    "summary.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
