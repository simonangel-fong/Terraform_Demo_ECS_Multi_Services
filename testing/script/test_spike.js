import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

export const errorRate = new Rate("errors");

const BASE = __ENV.BASE || "http://localhost:8000";
const RATE_WARMUP = Number(__ENV.RATE_WARMUP) || 5; // low, normal-ish rate
const RATE_SPIKE = Number(__ENV.RATE_SPIKE) || 200; // burst rate

// Durations (short total, 2–5 minutes)
const DURATION_WARMUP = __ENV.DURATION_WARMUP || "1m";
const DURATION_RAMP_UP = __ENV.DURATION_RAMP_UP || "10s"; // near-instant jump
const DURATION_SPIKE = __ENV.DURATION_SPIKE || "2m";
const DURATION_RAMP_DOWN = __ENV.DURATION_RAMP_DOWN || "1m";

const PRE_VU = Number(__ENV.PRE_VU) || 20;
const MAX_VU = Number(__ENV.MAX_VU) || 300;

const DEVICE_ID = __ENV.DEVICE_ID || "11111111-1111-1111-1111-111111111111";

export const options = {
  thresholds: {
    errors: ["rate<0.05"], // a bit more lenient than baseline
    http_req_failed: ["rate<0.05"], // spike will naturally stress the system

    // Latency
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
        { duration: DURATION_WARMUP, target: RATE_WARMUP }, // Warmup
        { duration: DURATION_RAMP_UP, target: RATE_SPIKE }, // Rapid ramp up
        { duration: DURATION_SPIKE, target: RATE_SPIKE }, // Hold the spike
        { duration: DURATION_RAMP_DOWN, target: RATE_WARMUP }, // ramp down
        { duration: "30s", target: 0 }, // ramp to zero
      ],
    },
  },

  cloud: {
    name: "Spike Testing",
  },
};

export default function () {
  // url: home
  const home_resp = http.get(`${BASE}`, {
    tags: { endpoint: "home" },
  });
  check(home_resp, {
    "home 200": (r) => r.status === 200,
  }) || errorRate.add(1);

  // url: health check
  const health_check_resp = http.get(`${BASE}/health`, {
    tags: { endpoint: "health_check" },
  });
  check(health_check_resp, {
    "health_check 200": (r) => r.status === 200,
  }) || errorRate.add(1);

  // url: list devices
  const list_device_resp = http.get(`${BASE}/devices`, {
    tags: { endpoint: "list_device" },
  });
  check(list_device_resp, {
    "list_device 200": (r) => r.status === 200,
    "list_device json array": (r) => {
      try {
        return Array.isArray(r.json());
      } catch (e) {
        return false;
      }
    },
  }) || errorRate.add(1);

  // url: get specific device
  if (DEVICE_ID) {
    const device_resp = http.get(`${BASE}/devices/${DEVICE_ID}`, {
      tags: { endpoint: "get_device" },
    });
    check(device_resp, {
      "get_device 200 or 404": (r) => r.status === 200 || r.status === 404,
    }) || errorRate.add(1);
  }
}

export function handleSummary(data) {
  return {
    "summary.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
