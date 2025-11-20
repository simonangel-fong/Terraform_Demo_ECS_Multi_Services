// test_smoke.js
import {
  getHome,
  getHealth,
  getDevices,
  getTelemetry,
  postTelemetry,
  errorRate,
} from "./target_url.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";

// ==============================
// Environment parameters
// ==============================
function parseNumberEnv(name, defaultValue) {
  const raw = __ENV[name];
  if (raw === undefined) return defaultValue;
  const n = Number(raw);
  return Number.isNaN(n) ? defaultValue : n;
}

const VU = parseNumberEnv("VU", 10); // # of devices
const DEVICE_INTERVAL = parseNumberEnv("DEVICE_INTERVAL", 10); // interval of hub request data
const RATE = Math.ceil(VU / DEVICE_INTERVAL); // rate
const DURATION = parseNumberEnv("DURATION", 1); // minute

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
    smoke_test: {
      executor: "constant-arrival-rate",
      preAllocatedVUs: VU,
      rate: RATE, // iterations per second
      duration: `${DURATION}m`,
      gracefulStop: "10s",
      exec: "smoke_test",
    },
  },
};

// ==============================
// Scenario function
// ==============================
export function smoke_test() {
  getHome();
  getHealth();
  getDevices();
  getTelemetry();
  postTelemetry();
}

export default smoke_test;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "summary_smoke.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
