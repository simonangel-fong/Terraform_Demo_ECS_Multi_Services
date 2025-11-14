import http from "k6/http";
import { check } from "k6";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

const ENDPOINT = __ENV.ENDPOINT || "http://localhost:8000";
const RATE = __ENV.RATE || 1000;
const DURATION = __ENV.DURATION || "2m";
const PRE_VUS = __ENV.PRE_VUS || 20; // start with more VUs
const MAX_VUS = __ENV.MAX_VUS || 200; // allow enough to reach high RPS

export const options = {
  thresholds: {
    "http_req_failed{endpoint:trips_list}": ["rate<0.01"], // Error rate < 1%
    "http_req_duration{endpoint:trips_list}": ["p(95)<800"], // p95 latency < 800 ms
  },

  scenarios: {
    ramp_rps: {
      executor: "ramping-arrival-rate",

      startRate: RATE * 0.1, // start at 100 iters/s
      timeUnit: "1s", // rate is "per second"

      preAllocatedVUs: PRE_VUS,
      maxVUs: MAX_VUS,

      stages: [
        // ramp up
        { duration: DURATION, target: RATE * 0.1 }, // warm-up @0.1 RATE RPS
        { duration: DURATION, target: RATE * 0.2 }, // hold 200 RPS
        { duration: DURATION, target: RATE * 0.4 }, // hold 400 RPS
        { duration: DURATION, target: RATE * 0.6 }, // hold 600 RPS
        { duration: DURATION, target: RATE * 0.8 }, // hold 800 RPS
        { duration: DURATION, target: RATE * 1 }, // push to 1000 RPS
      ],
    },
  },
};

export default function () {
  const res = http.get(`${ENDPOINT}/trips`, {
    tags: { endpoint: "trips_list", method: "GET" },
  });

  check(res, {
    "status is 200": (r) => r.status === 200,
    "json array": (r) => Array.isArray(r.json()),
  });
}

export function handleSummary(data) {
  return {
    "summary.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
