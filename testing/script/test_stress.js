import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

export const errorRate = new Rate("errors");

const BASE = __ENV.BASE || "http://localhost:8000";
const RATE = Number(__ENV.RATE) || 300; // highest RPS to push to
const DURATION = __ENV.DURATION || "3m"; // time spent at each level
const PRE_VU = Number(__ENV.PRE_VU) || 20;
const MAX_VU = Number(__ENV.MAX_VU) || 500;

const DEVICE_ID = __ENV.DEVICE_ID || "11111111-1111-1111-1111-111111111111";

export const options = {
  // thresholds
  thresholds: {
    checks: ["rate>0.99"], // 99% of checks must pass
    http_req_failed: [
      { threshold: "rate<0.80", abortOnFail: true }, // allow up to 80% failures "disaster"; abort when fail
    ],
    // errors: ["rate<0.80"],
  },

  scenarios: {
    stress: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,

      startRate: RATE * 0.1, // start at the first step
      stages: [
        { duration: DURATION, target: RATE * 0.1 },
        { duration: DURATION, target: RATE * 0.2 },
        { duration: DURATION, target: RATE * 0.3 },
        { duration: DURATION, target: RATE * 0.4 },
        { duration: DURATION, target: RATE * 0.5 },
        { duration: DURATION, target: RATE * 0.6 },
        { duration: DURATION, target: RATE * 0.7 },
        { duration: DURATION, target: RATE * 0.8 },
        { duration: DURATION, target: RATE * 0.9 },
        { duration: DURATION, target: RATE * 1.0 },
        { duration: DURATION, target: RATE * 1.0 },
        { duration: "30s", target: 0 }, // ramp to zero
      ],
    },
  },
  cloud: {
    name: "Stress Testing",
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
