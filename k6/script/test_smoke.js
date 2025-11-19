import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import {
  getHome,
  getHealth,
  getDevices,
  getTelemetry,
  postTelemetry,
  errorRate,
} from "./target_url.js";

// ==============================
// Environment parameters
// ==============================
function parseNumberEnv(name, defaultValue) {
  const raw = __ENV[name];
  if (raw === undefined) return defaultValue;
  const n = Number(raw);
  return Number.isNaN(n) ? defaultValue : n;
}

const DEVICE_VU = parseNumberEnv("DEVICE_VU", 50); // # of devices
const DEVICE_VU_MAX = parseNumberEnv("DEVICE_VU_MAX", 600); // max # of devices
const DEVICE_INTERVAL = parseNumberEnv("DEVICE_INTERVAL", 10); // interval of device transmit data
const DEVICE_RATE = DEVICE_VU / DEVICE_INTERVAL; // post rate
const DEVICE_RATE_MAX = DEVICE_VU_MAX / DEVICE_INTERVAL; // post max rate

const HUB_VU = parseNumberEnv("HUB_VU", 50); // # of hub
const HUB_VU_MAX = parseNumberEnv("HUB_VU_MAX", 600); // max # of hub
const HUB_INTERVAL = parseNumberEnv("HUB_INTERVAL", 10); // interval of hub request data
const HUB_RATE = HUB_VU / HUB_INTERVAL; // get rate
const HUB_RATE_MAX = HUB_VU_MAX / HUB_INTERVAL; // get max rate

const DURATION = parseNumberEnv("DURATION", 10);

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Smoke Testing",
  },
  thresholds: {
    errors: ["rate<0.01"], // Logical errors (failed checks)
    http_req_failed: ["rate<0.01"], // HTTP-level failures
    http_req_duration: ["p(95)<500"], // Global latency guardrail

    "http_req_duration{endpoint:home}": ["p(95)<200", "p(99)<500"], // Home latency
    "http_req_duration{endpoint:telemetry_post}": ["p(95)<500", "p(99)<1000"], // Post latency
  },

  scenarios: {
    smoke_home: {
      executor: "constant-arrival-rate",
      rate: DEVICE_RATE, // iterations per second
      duration: `${DURATION}s`,
      timeUnit: "1s",
      preAllocatedVUs: DEVICE_VU,
      maxVUs: DEVICE_VU_MAX,
      gracefulStop: "10s",
      exec: "smokeTest",
    },
  },
};

// ==============================
// Scenario function
// ==============================
export function smokeHome() {
  getHome();
  getHealth();
  getDevices();
  getTelemetry();
  postTelemetry();
}

export default smokeTest;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "summary_smoke.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
