// test_baseline.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { parseNumberEnv, getDeviceForVU } from "./common.js";
import { getTelemetryLatest, postTelemetry } from "./target_url.js";

// ==============================
// Environment parameters
// ==============================

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

const DEVICE_VU = parseNumberEnv("DEVICE_VU", 100); // # of devices
const DEVICE_INTERVAL = parseNumberEnv("DEVICE_INTERVAL", 10); // interval of device transmit data
const DEVICE_RATE = Math.ceil(DEVICE_VU / DEVICE_INTERVAL); // post rate

const HUB_VU = parseNumberEnv("HUB_VU", 10); // # of hub
const HUB_INTERVAL = parseNumberEnv("HUB_INTERVAL", 10); // interval of hub request data
const HUB_RATE = Math.ceil(HUB_VU / HUB_INTERVAL); // get rate

const DURATION = parseNumberEnv("DURATION", 1);

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Baseline Testing",
  },
  thresholds: {
    http_req_failed: ["rate<0.001"], // HTTP-level failures
    http_req_duration: ["p(95)<500"], // global latency

    // latency for telemetry POSTs
    "http_req_duration{endpoint:telemetry_post}": ["p(95)<100", "p(99)<200"],
  },

  scenarios: {
    // device
    baseline_telemetry_post: {
      executor: "constant-arrival-rate",
      preAllocatedVUs: DEVICE_VU,
      rate: DEVICE_RATE, // writes per second
      duration: `${DURATION}m`,
      gracefulStop: "30s",
      exec: "baseline_telemetry_post",
    },

    // dashboard
    baseline_telemetry_get_lastest: {
      executor: "constant-arrival-rate",
      preAllocatedVUs: HUB_VU,
      rate: HUB_RATE, // read per second
      duration: `${DURATION}m`,
      gracefulStop: "10s",
      exec: "baseline_telemetry_get_lastest",
    },
  },
};

// ==============================
// Scenario function
// ==============================
const device = getDeviceForVU();

export function baseline_telemetry_post() {
  postTelemetry({ base_url: BASE_URL, device });
}

export function baseline_telemetry_get_lastest() {
  getTelemetryLatest({ base_url: BASE_URL, device });
}

export default baseline_telemetry_post;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "summary_baseline.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
