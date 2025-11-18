// test_soak.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import {
  runGetApiTesting,
  runPostApiTesting,
  errorRate,
} from "./target_url.js";

const RATE_SOAK = Number(__ENV.RATE_SOAK) || 30;
const DURATION_RAMP = __ENV.DURATION_RAMP || "5m";
const DURATION_SOAK = __ENV.DURATION_SOAK || "2h";
const VU_PRE = Number(__ENV.VU_PRE) || 10;
const VU_MAX = Number(__ENV.VU_MAX) || 100;

export const options = {
  cloud: {
    name: "Soak Testing",
  },
  thresholds: {
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],

    "http_req_duration{endpoint:home}": ["p(95)<600", "p(99)<1200"],
    "http_req_duration{endpoint:health}": ["p(95)<400", "p(99)<800"],
    "http_req_duration{endpoint:list_devices}": ["p(95)<1000", "p(99)<2000"],
    "http_req_duration{endpoint:get_device_by_name_type}": [
      "p(95)<1500",
      "p(99)<2500",
    ],
    "http_req_duration{endpoint:latest_position}": ["p(95)<1200", "p(99)<2000"],
    "http_req_duration{endpoint:track_position}": ["p(95)<1500", "p(99)<2500"],
    "http_req_duration{endpoint:update_position}": ["p(95)<1200", "p(99)<2000"],
  },

  scenarios: {
    soak: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: VU_PRE,
      maxVUs: VU_MAX,
      startRate: 1,
      stages: [
        { duration: DURATION_RAMP, target: RATE_SOAK }, // warm up
        { duration: DURATION_SOAK, target: RATE_SOAK }, // long, steady load
        { duration: "2m", target: 0 }, // cool-down
      ],
      exec: "soakTest",
    },
  },
};

export function soakTest() {
  runGetApiTesting();
  runPostApiTesting();
}

export default soakTest;

export function handleSummary(data) {
  return {
    "summary_soak.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
