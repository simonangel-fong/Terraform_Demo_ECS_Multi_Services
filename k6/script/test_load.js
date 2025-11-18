// test_load.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { postTelemetry, getTelemetry, errorRate } from "./target_url.js";

// ==============================
// Environment parameters
// ==============================
function parseNumberEnv(name, defaultValue) {
  const raw = __ENV[name];
  if (raw === undefined) return defaultValue;
  const n = Number(raw);
  return Number.isNaN(n) ? defaultValue : n;
}

const VU_PRE = parseNumberEnv("VU_PRE", 50);
const VU_MAX = parseNumberEnv("VU_MAX", 600); // max # of devices
const VU_HUB = parseNumberEnv("VU_HUB", 50); // # of hub to monitor real time data
const INTERVAL_DEVICE = parseNumberEnv("INTERVAL_DEVICE", 20); // second; every 20s
const INTERVAL_HUB = parseNumberEnv("INTERVAL_HUB", 20); // second; every 20s
const DURATION = parseNumberEnv("DURATION", 20); // minute

// Rates are calculated by VU and interval
const RATE_POST = Math.ceil(VU_MAX / INTERVAL_DEVICE); // post QPS = devices / interval; 30 = 600 / 20
const RATE_GET = Math.ceil(VU_HUB / INTERVAL_HUB); // get QPS = hub / interval; 2.5 = 50 / 20

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Load Testing",
  },
  thresholds: {
    errors: ["rate<0.001"], // < 0.1% failed checks
    http_req_failed: ["rate<0.001"], // HTTP-level failures

    // post
    "http_req_duration{endpoint:telemetry_post}": [
      "p(50)<50", // median very fast
      "p(95)<100", // SLO target
      "p(99)<150", // 99
    ],

    // get
    "http_req_duration{endpoint:telemetry_get}": ["p(95)<200", "p(99)<400"],
  },

  scenarios: {
    // devices
    postTelemetry: {
      executor: "constant-arrival-rate",
      rate: RATE_POST, // post rate
      timeUnit: "1s",
      duration: `${DURATION}m`,
      preAllocatedVUs: VU_PRE,
      maxVUs: VU_MAX,
      gracefulStop: "30s",
      exec: "loadTestPost",
    },

    // hub dashboard
    getTelemetry: {
      executor: "constant-arrival-rate",
      rate: RATE_GET, // get rate
      timeUnit: "1s",
      duration: `${DURATION}m`,
      preAllocatedVUs: VU_HUB,
      maxVUs: VU_HUB,
      gracefulStop: "30s",
      exec: "loadTestGet",
    },
  },
};

// ==============================
// Scenario function
// ==============================
export function loadTestPost() {
  postTelemetry();
}

export function loadTestGet() {
  getTelemetry();
}

export default loadTestPost;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "load_test.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
