// test_stress.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { parseNumberEnv, getDeviceForVU } from "./common.js";
import { getTelemetryLatest, postTelemetry } from "./target_url.js";

// ==============================
// Environment
// ==============================
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

const DEVICE_VU = parseNumberEnv("DEVICE_VU", 2000); // # of devices
const DEVICE_INTERVAL = parseNumberEnv("DEVICE_INTERVAL", 10); // interval of device transmit data
const DEVICE_RATE = Math.ceil(DEVICE_VU / DEVICE_INTERVAL); // post rate

const HUB_VU = Math.ceil(DEVICE_VU * 0.1); // # of hub
const HUB_INTERVAL = parseNumberEnv("HUB_INTERVAL", 10); // interval of hub request data
const HUB_RATE = Math.ceil(HUB_VU / HUB_INTERVAL); // get rate

const DURATION_STAGE = parseNumberEnv("DURATION_STAGE", 3); // minute;

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Stress Test",
  },
  thresholds: {
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
    // post
    stress_telemetry_post: {
      executor: "ramping-arrival-rate",
      preAllocatedVUs: DEVICE_VU,
      stages: [
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.1 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.1 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.2 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.2 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.3 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.3 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.4 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.4 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.5 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.5 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.6 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.6 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.7 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.7 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.8 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.8 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.9 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 0.9 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 1 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 1 },
        { duration: `${DURATION_STAGE}m`, target: DEVICE_RATE * 1 },
      ],

      gracefulStop: "60s",
      exec: "stress_telemetry_post",
    },

    // get
    stress_telemetry_get: {
      executor: "ramping-arrival-rate",
      preAllocatedVUs: HUB_VU,
      stages: [
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.1) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.1) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.2) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.2) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.3) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.3) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.4) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.4) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.5) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.5) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.6) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.6) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.7) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.7) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.8) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.8) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.9) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 0.9) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 1) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 1) },
        { duration: `${DURATION_STAGE}m`, target: Math.ceil(HUB_RATE * 1) },
      ],

      gracefulStop: "60s",
      exec: "stress_telemetry_get",
    },
  },
};

// ==============================
// Scenario functions
// ==============================
const device = getDeviceForVU();

export function stress_telemetry_post() {
  postTelemetry({ base_url: BASE_URL, device });
}

export function stress_telemetry_get() {
  getTelemetryLatest({ base_url: BASE_URL, device });
}

export default stress_telemetry_post;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "stress_test.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
