// test_soak.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { runApiTesting, errorRate } from "./target_url.js";

const RATE_SOAK = Number(__ENV.RATE_SOAK) || 30;
const DURATION_RAMP = __ENV.DURATION_RAMP || "5m";
const DURATION_SOAK = __ENV.DURATION_SOAK || "2h";
const PRE_VU = Number(__ENV.PRE_VU) || 10;
const MAX_VU = Number(__ENV.MAX_VU) || 100;

export const options = {
  cloud: {
    name: "Soak Testing",
  },
  thresholds: {
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],

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
        { duration: DURATION_RAMP, target: RATE_SOAK }, // warm up
        { duration: DURATION_SOAK, target: RATE_SOAK }, // long, steady
        { duration: "2m", target: 0 }, // cool-down
      ],
    },
  },
};

export default function () {
  runApiTesting();
}

export function handleSummary(data) {
  return {
    "summary_soak.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
