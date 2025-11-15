// test_baseline.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { runApiTesting, errorRate } from "./target_url.js";

const RATE = Number(__ENV.RATE) || 50;
const DURATION_RAMP = __ENV.DURATION_RAMP || "5m"; // ramp up
const DURATION_HOLD = __ENV.DURATION_HOLD || "10m"; // steady
const PRE_VU = Number(__ENV.PRE_VU) || 10;
const MAX_VU = Number(__ENV.MAX_VU) || 100;

export const options = {
  cloud: {
    name: "Baseline (Ramp-up) Testing",
  },
  thresholds: {
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],

    // SLO: latency per endpoint
    "http_req_duration{endpoint:home}": [
      "p(50)<200",
      "p(95)<500",
      "p(99)<1000",
    ],
    "http_req_duration{endpoint:health_check}": [
      "p(50)<100",
      "p(95)<300",
      "p(99)<800",
    ],
    "http_req_duration{endpoint:list_device}": [
      "p(50)<300",
      "p(95)<800",
      "p(99)<1500",
    ],
    "http_req_duration{endpoint:get_device}": [
      "p(50)<300",
      "p(95)<1000",
      "p(99)<2000",
    ],
  },

  scenarios: {
    baseline_ramp: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
      startRate: 1,
      stages: [
        { duration: DURATION_RAMP, target: RATE }, // ramp up
        { duration: DURATION_HOLD, target: RATE }, // hold
        { duration: "2m", target: 0 }, // ramp down
      ],
    },
  },
};

export default function () {
  runApiTesting();
}

export function handleSummary(data) {
  return {
    "summary_baseline.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
