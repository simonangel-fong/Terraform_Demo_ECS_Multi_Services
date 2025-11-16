// test_baseline.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import {
  runGetApiTesting,
  runPostApiTesting,
  errorRate,
} from "./target_url.js";

// Base total rate
const RATE = Number(__ENV.RATE) || 50;

const RATE_GET = Number(__ENV.RATE_GET) || Math.max(1, Math.round(RATE * 0.3)); // ~30% reads
const RATE_POST = Number(__ENV.RATE_POST) || RATE;                               // ~100% baseline writes

const DURATION_RAMP = __ENV.DURATION_RAMP || "5m";   // ramp up
const DURATION_HOLD = __ENV.DURATION_HOLD || "10m";  // steady
const PRE_VU = Number(__ENV.PRE_VU) || 10;
const MAX_VU = Number(__ENV.MAX_VU) || 100;

export const options = {
  cloud: {
    name: "Baseline (Ramp-up) Testing",
  },
  thresholds: {
    // failure rates
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],

    // SLO: latency per endpoint
    "http_req_duration{endpoint:home}": [
      "p(50)<200",
      "p(95)<500",
      "p(99)<1000",
    ],
    "http_req_duration{endpoint:healthz}": [
      "p(50)<100",
      "p(95)<300",
      "p(99)<800",
    ],
    "http_req_duration{endpoint:list_devices}": [
      "p(50)<300",
      "p(95)<800",
      "p(99)<1500",
    ],
    "http_req_duration{endpoint:get_device_by_name_type}": [
      "p(50)<300",
      "p(95)<1000",
      "p(99)<2000",
    ],
    "http_req_duration{endpoint:latest_position}": [
      "p(50)<300",
      "p(95)<800",
      "p(99)<1500",
    ],
    "http_req_duration{endpoint:track_position}": [
      "p(50)<400",
      "p(95)<1200",
      "p(99)<2500",
    ],
    "http_req_duration{endpoint:update_position}": [
      "p(50)<300",
      "p(95)<800",
      "p(99)<1500",
    ],
  },

  scenarios: {
    // Read / query traffic (GET endpoints)
    baseline_get: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
      startRate: 1,
      stages: [
        { duration: DURATION_RAMP, target: RATE_GET },  // ramp up reads
        { duration: DURATION_HOLD, target: RATE_GET },  // hold reads
        { duration: "2m", target: 0 },                  // ramp down reads
      ],
      exec: "getTest",
    },

    // Write traffic (POST /device/position/{device_id})
    baseline_post: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
      startRate: 1,
      stages: [
        { duration: DURATION_RAMP, target: RATE_POST }, // ramp up writes
        { duration: DURATION_HOLD, target: RATE_POST }, // hold writes
        { duration: "2m", target: 0 },                  // ramp down writes
      ],
      exec: "postTest",
    },
  },
};

// Scenario entrypoints
export function getTest() {
  runGetApiTesting();
}

export function postTest() {
  runPostApiTesting();
}

export default function () {
  runGetApiTesting();
  runPostApiTesting();
}

export function handleSummary(data) {
  return {
    "summary_baseline.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
