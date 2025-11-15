// test_smoke.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { runApiTesting, errorRate } from "./target_url.js";

const RATE = Number(__ENV.RATE) || 5;
const DURATION = Number(__ENV.DURATION) || 60;
const PRE_VU = Number(__ENV.PRE_VU) || 3;
const MAX_VU = Number(__ENV.MAX_VU) || 10;

export const options = {
  cloud: {
    name: "Smoke Testing",
  },
  thresholds: {
    errors: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],
  },

  scenarios: {
    smoke: {
      executor: "constant-arrival-rate",
      rate: RATE,
      duration: `${DURATION}s`,
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
    },
  },
};

export default function () {
  runApiTesting();
}

export function handleSummary(data) {
  return {
    "summary_smoke.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
