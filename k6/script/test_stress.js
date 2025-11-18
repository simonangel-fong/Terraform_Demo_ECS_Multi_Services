// test_stress.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import {
  runGetApiTesting,
  runPostApiTesting,
  errorRate,
} from "./target_url.js";

const RATE = Number(__ENV.RATE) || 300;          // highest RPS target
const DURATION = __ENV.DURATION || "3m";         // per step
const PRE_VU = Number(__ENV.PRE_VU) || 20;
const MAX_VU = Number(__ENV.MAX_VU) || 500;

export const options = {
  cloud: {
    name: "Stress Testing",
  },
  thresholds: {
    // checks pass
    checks: ["rate>0.99"],

    // Abort if failing
    http_req_failed: [{ threshold: "rate<0.80", abortOnFail: true }],

    // errors: ["rate<0.80"],
  },

  scenarios: {
    stress: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: PRE_VU,
      maxVUs: MAX_VU,
      startRate: RATE * 0.1,
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
        { duration: DURATION, target: RATE * 1.0 }, // sustain highest load
        { duration: "30s", target: 0 },             // cool down
      ],
      exec: "stressTest",
    },
  },
};

export function stressTest() {
  // both read & write paths in a stress iteration, 
  runGetApiTesting();
  runPostApiTesting();
}

export default stressTest;

export function handleSummary(data) {
  return {
    "summary_stress.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
