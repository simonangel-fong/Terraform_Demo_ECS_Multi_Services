import http from "k6/http";
import { check, sleep } from "k6";
import { randomString } from "https://jslib.k6.io/k6-utils/1.4.0/index.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  scenarios: {
    mix_rate: {
      executor: "constant-arrival-rate",
      rate: Number(__ENV.RATE || 200), // try 200 RPS first
      timeUnit: "1s",
      duration: __ENV.DURATION || "60s",
      preAllocatedVUs: Number(__ENV.PRE_VUS || 200),
      maxVUs: Number(__ENV.MAX_VUS || 1000),
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.02"], // <2% across all ops
    "http_req_duration{op:create}": ["p(95)<300"],
    "http_req_duration{op:get}": ["p(95)<200"],
    "http_req_duration{op:delete}": ["p(95)<300"],
  },
};

export default function () {
  // 1) CREATE
  const payload = JSON.stringify({
    start_station: `k6-station-${randomString(6)}`,
  });
  const params = { headers: { "Content-Type": "application/json" } };

  const create = http.post(`${BASE_URL}/trips`, payload, {
    ...params,
    tags: { op: "create", endpoint: "trips" },
  });

  check(create, {
    "create 201": (r) => r.status === 201,
    "create has id": (r) => r.json("trip_id") !== undefined,
  });

  if (create.status !== 201) return; // fail fast for this iter

  const id = create.json("trip_id");

  // 2) GET one
  const getOne = http.get(`${BASE_URL}/trips/${id}`, {
    tags: { op: "get", endpoint: "trip_id" },
  });
  check(getOne, {
    "get 200": (r) => r.status === 200,
    "id matches": (r) => r.json("trip_id") === id,
  });

  // 3) DELETE
  const del = http.del(`${BASE_URL}/trips/${id}`, null, {
    tags: { op: "delete", endpoint: "trip_id" },
  });
  check(del, { "delete 204": (r) => r.status === 204 });

  // tiny think-time (keeps connection reuse healthy)
  sleep(0.05);
}

export function handleSummary(data) {
  return {
    "summary.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
