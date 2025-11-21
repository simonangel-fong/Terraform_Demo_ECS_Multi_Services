// test_soak.js
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.4/index.js";
import { parseNumberEnv, getDeviceForVU } from "./common.js";
import { getTelemetryLatest, postTelemetry } from "./target_url.js";

// ==============================
// Environment parameters
// ==============================
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

const DEVICE_VU = parseNumberEnv("DEVICE_VU", 600); // # of devices
const DEVICE_INTERVAL = parseNumberEnv("DEVICE_INTERVAL", 10); // interval of device transmit data
const DEVICE_RATE = Math.ceil(DEVICE_VU / DEVICE_INTERVAL); // post rate

const HUB_VU = parseNumberEnv("HUB_VU", 60); // # of hub
const HUB_INTERVAL = parseNumberEnv("HUB_INTERVAL", 10); // interval of hub request data
const HUB_RATE = Math.ceil(HUB_VU / HUB_INTERVAL); // get rate

const DURATION = parseNumberEnv("DURATION", 120); // minute

// ==============================
// k6 options
// ==============================
export const options = {
  cloud: {
    name: "Load Testing",
  },
  thresholds: {
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
    soak_telemetry_post: {
      executor: "constant-arrival-rate",
      preAllocatedVUs: DEVICE_VU,
      rate: DEVICE_RATE, // post rate
      duration: `${DURATION}m`,
      gracefulStop: "30s",
      exec: "soak_telemetry_post",
    },

    // hub dashboard
    soak_telemetry_get: {
      executor: "constant-arrival-rate",
      preAllocatedVUs: HUB_VU,
      rate: HUB_RATE, // get rate
      duration: `${DURATION}m`,
      gracefulStop: "30s",
      exec: "soak_telemetry_get",
    },
  },
};

// ==============================
// Scenario function
// ==============================
const device = getDeviceForVU();

export function soak_telemetry_post() {
  postTelemetry({ base_url: BASE_URL, device });
}

export function soak_telemetry_get() {
  getTelemetryLatest({ base_url: BASE_URL, device });
}

export default soak_telemetry_post;

// ==============================
// Summary output
// ==============================
export function handleSummary(data) {
  return {
    "load_test.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
