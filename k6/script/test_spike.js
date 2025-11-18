// test_spike.js
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

const VU_DEVICE = parseNumberEnv("VU_DEVICE", 50);  // # of devices
const VU_DEVICE_MAX = parseNumberEnv("VU_DEVICE_MAX", 600); // max # of devices
const VU_HUB = parseNumberEnv("VU_HUB", 10); // # of hub to monitor real time data
const VU_HUB_MAX = parseNumberEnv("VU_HUB_MAX", 30); // max # of hub to monitor real time data

const RATE_POST = parseNumberEnv("RATE_POST", 30); // baseline post
const RATE_POST_MAX = parseNumberEnv("RATE_POST_MAX", 90); // max post

const RATE_GET = parseNumberEnv("RATE_GET", 5); // baseline get
const RATE_GET_MAX = parseNumberEnv("RATE_GET_MAX", 15); // max get

const DURATION_UP = parseNumberEnv("DURATION_UP", 300); // second; warm up
const DURATION_DOWN = parseNumberEnv("DURATION_DOWN", 600); // second; recovery
const DURATION_SPIKE = parseNumberEnv("DURATION_SPIKE", 300); // second; hold on spike

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Spike Test",
  },
  thresholds: {
    errors: ["rate<0.01"], // < 0.01 error rate
    http_req_failed: ["rate<0.01"], // HTTP-level failures

    // Writes: POST /telemetry
    "http_req_duration{endpoint:telemetry_post}": [
      "p(50)<100", // median can be a bit higher
      "p(95)<200", // main spike SLO: p95 < 200ms
      "p(99)<400",
    ],

    // Reads: GET /telemetry (dashboards)
    "http_req_duration{endpoint:telemetry_get}": ["p(95)<250", "p(99)<500"],
  },

  scenarios: {
    // post
    post_spike: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: VU_DEVICE,
      maxVUs: VU_DEVICE_MAX,
      startRate: RATE_POST, // start at baseline

      stages: [
        { duration: `${DURATION_UP}s`, target: RATE_POST },  //Warmup
        { duration: "10s", target: RATE_POST_MAX }, // ramp up
        { duration: `${DURATION_SPIKE}s`, target: RATE_POST_MAX }, // Hold spike
        { duration: "10s", target: RATE_POST }, // drop back
        { duration: `${DURATION_DOWN}s`, target: RATE_POST }, // Recovery
      ],
      gracefulStop: "30s",
      exec: "spikePost",
    },

    // get
    get_spike: {
      executor: "ramping-arrival-rate",
      timeUnit: "1s",
      preAllocatedVUs: VU_HUB,
      maxVUs: VU_HUB_MAX,
      startRate: RATE_GET, // start at baseline

      stages: [
        { duration: `${DURATION_UP}s`, target: RATE_GET },  //Warmup
        { duration: "10s", target: RATE_GET_MAX }, // ramp up
        { duration: `${DURATION_SPIKE}s`, target: RATE_GET_MAX }, // Hold spike
        { duration: "10s", target: RATE_GET }, // drop back
        { duration: `${DURATION_DOWN}s`, target: RATE_GET }, // Recovery
      ],
      gracefulStop: "30s",
      exec: "spikeGet",
    },
  },
};

// ==============================
// Scenario functions
// ==============================
export function spikePost() {
  postTelemetry();
}

export function spikeGet() {
  getTelemetry();
}

// Optional default (ignored when scenarios are present, but OK to keep)
export default spikePost;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "spike_test.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
