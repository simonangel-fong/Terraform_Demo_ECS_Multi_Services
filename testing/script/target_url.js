// common.js
import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

// ---- Shared custom metric ----
export const errorRate = new Rate("errors");

// ---- Shared env config ----
export const BASE = __ENV.BASE || "http://localhost:8000";
export const DEVICE_ID =
  __ENV.DEVICE_ID || "11111111-1111-1111-1111-111111111111";

/**
 * API endpoint to test
 * - home
 * - health
 * - list devices
 * - get device
 *
 * If a check fails, we increment `errorRate`.
 */
export function runApiTesting() {
  // ---- home ----
  const home_resp = http.get(`${BASE}`, {
    tags: { endpoint: "home" },
  });

  const homeOk = check(home_resp, {
    "home 200": (r) => r.status === 200,
  });

  if (!homeOk) {
    errorRate.add(1);
  }

  // ---- health ----
  const health_resp = http.get(`${BASE}/health`, {
    tags: { endpoint: "health_check" },
  });

  const healthOk = check(health_resp, {
    "health_check 200": (r) => r.status === 200,
  });

  if (!healthOk) {
    errorRate.add(1);
  }

  // ---- list devices ----
  const list_device_resp = http.get(`${BASE}/devices`, {
    tags: { endpoint: "list_device" },
  });

  const listOk = check(list_device_resp, {
    "list_device 200": (r) => r.status === 200,
    "list_device json array": (r) => {
      try {
        return Array.isArray(r.json());
      } catch (e) {
        return false;
      }
    },
  });

  if (!listOk) {
    errorRate.add(1);
  }

  // ---- get device ----
  const device_resp = http.get(`${BASE}/devices/${DEVICE_ID}`, {
    tags: { endpoint: "get_device" },
  });

  const deviceOk = check(device_resp, {
    "get_device 200 or 404": (r) => r.status === 200 || r.status === 404,
  });

  if (!deviceOk) {
    errorRate.add(1);
  }
}
