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

const DEVICE_VU = parseNumberEnv("DEVICE_VU", 600); // # of devices
const DEVICE_INTERVAL = parseNumberEnv("DEVICE_INTERVAL", 10); // interval of device transmit data
const DEVICE_RATE = Math.ceil(DEVICE_VU / DEVICE_INTERVAL); // post rate
const DEVICE_RATE_SPIKE = DEVICE_RATE * 3; // spike rate

const HUB_VU = parseNumberEnv("HUB_VU", 60); // # of hub
const HUB_INTERVAL = parseNumberEnv("HUB_INTERVAL", 10); // interval of hub request data
const HUB_RATE = Math.ceil(HUB_VU / HUB_INTERVAL); // get rate
const HUB_RATE_SPIKE = HUB_RATE * 3; // spike rate

const DURATION_WARM = parseNumberEnv("DURATION_WARM", 1); // second; warm up
const DURATION_SPIKE = parseNumberEnv("DURATION_SPIKE", 3); // second; hold on spike
const DURATION_COOL = parseNumberEnv("DURATION_COOL", 1); // second; cool down

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
    spike_telemetry_post: {
      executor: "ramping-arrival-rate",
      preAllocatedVUs: DEVICE_VU,
      startRate: DEVICE_RATE, // start at baseline
      timeUnit: "1s",

      stages: [
        { duration: `${DURATION_WARM}m`, target: DEVICE_RATE }, //Warmup
        { duration: "10s", target: DEVICE_RATE_SPIKE }, // ramp up
        { duration: `${DURATION_SPIKE}m`, target: DEVICE_RATE_SPIKE }, // Hold spike
        { duration: "10s", target: DEVICE_RATE }, // drop back
        { duration: `${DURATION_COOL}m`, target: DEVICE_RATE }, // Recovery
      ],
      gracefulStop: "30s",
      exec: "spike_telemetry_post",
    },

    // get
    spike_telemetry_get: {
      executor: "ramping-arrival-rate",
      preAllocatedVUs: HUB_VU,
      startRate: HUB_RATE, // start at baseline
      timeUnit: "1s",

      stages: [
        { duration: `${DURATION_WARM}m`, target: HUB_RATE }, //Warmup
        { duration: "10s", target: HUB_RATE_SPIKE }, // ramp up
        { duration: `${DURATION_SPIKE}m`, target: HUB_RATE_SPIKE }, // Hold spike
        { duration: "10s", target: HUB_RATE }, // drop back
        { duration: `${DURATION_COOL}m`, target: HUB_RATE }, // Recovery
      ],
      gracefulStop: "30s",
      exec: "spike_telemetry_get",
    },
  },
};

// ==============================
// Scenario functions
// ==============================
export function spike_telemetry_post() {
  postTelemetry();
}

export function spike_telemetry_get() {
  getTelemetry();
}

// Optional default (ignored when scenarios are present, but OK to keep)
export default spike_telemetry_post;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "spike_test.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
