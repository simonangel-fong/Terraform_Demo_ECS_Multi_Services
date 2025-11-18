// test_baseline_phase1.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { postTelemetry, errorRate } from "./target_url.js";

// ==============================
// Environment parameters
// ==============================
function parseNumberEnv(name, defaultValue) {
  const raw = __ENV[name];
  if (raw === undefined) return defaultValue;
  const n = Number(raw);
  return Number.isNaN(n) ? defaultValue : n;
}

const RATE = parseNumberEnv("RATE", 10); // RATE 10 = 200 devices / every 20s
const DURATION = parseNumberEnv("DURATION", 600); // second
const VU_PRE = parseNumberEnv("VU_PRE", 20); // at least 20 devices
const VU_MAX = parseNumberEnv("VU_MAX", 200); // max 200 devices

const DURATION_MINUTES = parseNumberEnv("DURATION_MINUTES", 45);

// ==============================
// k6 options
// ==============================

export const options = {
  cloud: {
    name: "Baseline Testing",
  },
  thresholds: {
    errors: ["rate<0.001"], // < 0.1% failed checks
    http_req_failed: ["rate<0.001"], // HTTP-level failures
    http_req_duration: ["p(95)<500"], // global latency

    // latency for telemetry POSTs
    "http_req_duration{endpoint:telemetry_post}": ["p(95)<100", "p(99)<200"],
  },

  scenarios: {
    baseline_phase1: {
      executor: "constant-arrival-rate",
      rate: RATE, // writes per second
      timeUnit: "1s",
      duration: `${DURATION}s`,
      preAllocatedVUs: VU_PRE,
      maxVUs: VU_MAX,
      gracefulStop: "30s",
      exec: "baselineTest",
    },
  },
};

// ==============================
// Scenario function
// ==============================
export function baselineTest() {
  postTelemetry(); // post heavy
}

export default baselineTest;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "summary_baseline_phase1.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
