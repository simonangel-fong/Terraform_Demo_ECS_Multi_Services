import http from "k6/http";
import { check } from "k6";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

const DOMAIN = __ENV.DOMAIN || "localhost";
const BASE_URL = `${DOMAIN}`;
const RATE = __ENV.RATE || 100;
const DURATION = __ENV.DURATION || "60s";
const PRE_VUS = __ENV.PRE_VUS || 1;
const MAX_VUS = __ENV.MAX_VUS || 10;

export const options = {
  thresholds: {
    "http_req_failed{endpoint:trips_list}": ["rate<0.01"], // <1% errors
    "http_req_duration{endpoint:trips_list}": ["p(95)<800"], // p95 < 200ms
  },
  scenarios: {
    read_high_rps: {
      executor: "constant-arrival-rate",
      rate: RATE, // Number of iterations per 1s
      duration: DURATION, // test length
      preAllocatedVUs: PRE_VUS, // pre-spawned VUs
      maxVUs: MAX_VUS,
    },
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
