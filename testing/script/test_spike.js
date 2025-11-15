// test_spike.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { runApiTesting, errorRate } from "./target_url.js";

const RATE_WARMUP = Number(__ENV.RATE_WARMUP) || 5;
const RATE_SPIKE = Number(__ENV.RATE_SPIKE) || 200;

const DURATION_WARMUP = __ENV.DURATION_WARMUP || "1m";
const DURATION_RAMP_UP = __ENV.DURATION_RAMP_UP || "10s";
const DURATION_SPIKE = __ENV.DURATION_SPIKE || "2m";
const DURATION_RAMP_DOWN = __ENV.DURATION_RAMP_DOWN || "1m";

const PRE_VU = Number(__ENV.PRE_VU) || 20;
const MAX_VU = Number(__ENV.MAX_VU) || 300;

export const options = {
  cloud: {
    name: "Spike Testing",
  },
  thresholds: {
    errors: ["rate<0.05"],
    http_req_failed: ["rate<0.05"],

    "http_req_duration{endpoint:home}": ["p(95)<2000"],
    "http_req_duration{endpoint:health_check}": ["p(95)<1500"],
    "http_req_duration{endpoint:list_device}": ["p(95)<3000"],
    "http_req_duration{endpoint:get_device}": ["p(95)<4000"],
  },

  scenarios: {
    spike: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
      startRate: RATE_WARMUP,
      stages: [
        { duration: DURATION_WARMUP, target: RATE_WARMUP },
        { duration: DURATION_RAMP_UP, target: RATE_SPIKE },
        { duration: DURATION_SPIKE, target: RATE_SPIKE },
        { duration: DURATION_RAMP_DOWN, target: RATE_WARMUP },
        { duration: "30s", target: 0 },
      ],
    },
  },
};

export default function () {
  runApiTesting();
}

export function handleSummary(data) {
  return {
    "summary_spike.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
