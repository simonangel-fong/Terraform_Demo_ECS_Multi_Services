// test_stress.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { postTelemetry, getTelemetry, errorRate } from "./target_url.js";

// ==============================
// Environment
// ==============================
function parseNumberEnv(name, defaultValue) {
  const raw = __ENV[name];
  if (raw === undefined) return defaultValue;
  const n = Number(raw);
  return Number.isNaN(n) ? defaultValue : n;
}

const VU_DEVICE = parseNumberEnv("VU_DEVICE", 50); // # of devices
const VU_DEVICE_MAX = parseNumberEnv("VU_DEVICE_MAX", 600); // max # of devices
const VU_HUB = parseNumberEnv("VU_HUB", 10); // # of hub to monitor real time data
const VU_HUB_MAX = parseNumberEnv("VU_HUB_MAX", 30); // max # of hub to monitor real time data

const RATE_POST = parseNumberEnv("RATE_POST", 50); // baseline post
const RATE_POST_MAX = parseNumberEnv("RATE_POST_MAX", 600); // max post

const RATE_GET = parseNumberEnv("RATE_GET", 5); // baseline get; baseline post/10
const RATE_GET_MAX = parseNumberEnv("RATE_GET_MAX", 60); // max get; max post/10

const DURATION_UP = parseNumberEnv("DURATION_UP", 60 * 30); // second;
const DURATION_DOWN = parseNumberEnv("DURATION_DOWN", 60 * 10); // second;
const DURATION_HOLD = parseNumberEnv("DURATION_HOLD", 60 * 10); // second;

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Stress Test",
  },
  thresholds: {
    errors: [
      {
        threshold: "rate<0.2",
        abortOnFail: true,
        delayAbortEval: "1m",
      },
    ],

    http_req_failed: [
      {
        threshold: "rate<0.1",
        abortOnFail: true,
        delayAbortEval: "1m",
      },
    ],

    // Writes: POST /telemetry
    "http_req_duration{endpoint:telemetry_post}": [
      "p(50)<150", // median
      "p(95)<400", // stress p95 upper bound
      "p(99)<800", // stress p99 upper bound
    ],

    // Reads: GET /telemetry (dashboards)
    "http_req_duration{endpoint:telemetry_get}": [
      "p(95)<600", // dashboards may be slower under stress
      "p(99)<1000",
    ],
  },

  scenarios: {
    // Stressing writes (POST /telemetry)
    stress_post_telemetry: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: VU_DEVICE,
      maxVUs: VU_DEVICE_MAX,
      startRate: RATE_POST,

      // With defaults: total ≈ 50 minutes (30 up + 10 hold + 10 down)
      stages: [
        { duration: `${DURATION_UP}s`, target: RATE_POST_MAX },
        { duration: `${DURATION_HOLD}s`, target: RATE_POST_MAX },
        { duration: `${DURATION_DOWN}s`, target: RATE_POST },
      ],

      gracefulStop: "60s",
      exec: "stress_post_telemetry",
    },

    // Stressing reads (GET /telemetry)
    stress_get_telemetry: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: VU_HUB,
      maxVUs: VU_HUB_MAX,
      startRate: RATE_GET,

      stages: [
        { duration: `${DURATION_UP}s`, target: RATE_GET_MAX },
        { duration: `${DURATION_HOLD}s`, target: RATE_GET_MAX },
        { duration: `${DURATION_DOWN}s`, target: RATE_GET },
      ],

      gracefulStop: "60s",
      exec: "stress_get_telemetry",
    },
  },
};

// ==============================
// Scenario functions
// ==============================
export function stress_post_telemetry() {
  postTelemetry();
}

export function stress_get_telemetry() {
  getTelemetry();
}

export default stress_post_telemetry;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "stress_test.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
