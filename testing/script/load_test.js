import http from "k6/http";
import { check } from "k6";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

const ENDPOINT = __ENV.ENDPOINT || "http://localhost:8000";
const VUS = __ENV.VUS || 50; // start with more VUs

export const options = {
  thresholds: {
    "http_req_failed{endpoint:trips_list}": ["rate<0.01"], // <1% errors
    "http_req_duration{endpoint:trips_list}": ["p(95)<800"], // p95 < 200ms
  },

  stages: [
    { duration: "1m", target: VUS * 0.2 }, // warm up: go from 0 → 10 VUs over 1 min
    { duration: "3m", target: VUS * 1 }, // ramp up: 10 → 50 VUs over 3 min
    { duration: "5m", target: VUS * 1 }, // steady load: hold 50 VUs for 5 min
    { duration: "1m", target: 0 }, // ramp down: 50 → 0 VUs over 1 min
  ],
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
G;
