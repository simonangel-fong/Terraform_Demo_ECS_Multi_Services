import http from "k6/http";
import { check } from "k6";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  scenarios: {
    read_high_rps: {
      executor: "constant-arrival-rate",
      rate: Number(__ENV.RATE || 10000), // target RPS (e.g., 1000/5000/10000)
      timeUnit: "1s",
      duration: __ENV.DURATION || "60s", // test length
      preAllocatedVUs: Number(__ENV.PRE_VUS || 2000), // pre-spawned VUs
      maxVUs: Number(__ENV.MAX_VUS || 5000),
    },
  },
  thresholds: {
    "http_req_failed{endpoint:trips_list}": ["rate<0.01"], // <1% errors
    "http_req_duration{endpoint:trips_list}": ["p(95)<200"], // p95 < 200ms (tune to your SLO)
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/trips`, {
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
