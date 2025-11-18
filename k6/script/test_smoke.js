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

const RATE = parseNumberEnv("RATE", 2); // iterations per second
const DURATION = parseNumberEnv("DURATION", 60); // seconds

const VU_PRE = parseNumberEnv("VU_PRE", 3);
const VU_MAX = parseNumberEnv("VU_MAX", 10);

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
    smoke: {
      executor: "constant-arrival-rate",
      rate: RATE, // iterations per second
      duration: `${DURATION}s`,
      timeUnit: "1s",
      preAllocatedVUs: VU_PRE,
      maxVUs: VU_MAX,
      gracefulStop: "10s",
      exec: "smokeTest",
    },
  },
};

// ==============================
// Scenario function
// ==============================
export function smokeTest() {
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
