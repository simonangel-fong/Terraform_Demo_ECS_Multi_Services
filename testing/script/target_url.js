// common.js
import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

// ---- custom metric ----
export const errorRate = new Rate("errors");

// ---- env config ----
export const BASE = __ENV.BASE || "http://localhost:8000";

// get device: name + type
export const DEVICE_NAME = __ENV.DEVICE_NAME || "device-001";
export const DEVICE_TYPE = __ENV.DEVICE_TYPE || "sensor";

// device_id
export const DEVICE_ID = __ENV.DEVICE_ID || "1";

/**
 * Run all GET endpoints:
 * - GET /
 * - GET /healthz
 * - GET /devices
 * - GET /devices/info?name=...&type=...
 * - GET /device/position/last/{device_id}
 * - GET /device/position/track/{device_id}?sec=10
 */
export function runGetApiTesting() {
  // ---- home ----
  const homeResp = http.get(`${BASE}`, {
    tags: { endpoint: "home" },
  });

  const homeOk = check(homeResp, {
    "home 200": (r) => r.status === 200,
  });
  if (!homeOk) {
    errorRate.add(1);
  }

  // ---- healthz ----
  const healthResp = http.get(`${BASE}/healthz`, {
    tags: { endpoint: "healthz" },
  });

  const healthOk = check(healthResp, {
    "healthz 200": (r) => r.status === 200,
  });
  if (!healthOk) {
    errorRate.add(1);
  }

  // ---- list devices ----
  const listResp = http.get(`${BASE}/devices`, {
    tags: { endpoint: "list_devices" },
  });

  const listOk = check(listResp, {
    "list_devices 200": (r) => r.status === 200,
    "list_devices json array": (r) => {
      try {
        return Array.isArray(r.json());
      } catch (_e) {
        return false;
      }
    },
  });
  if (!listOk) {
    errorRate.add(1);
  }

  // ---- get device by name + type ----
  const deviceInfoUrl = `${BASE}/devices/info?name=${encodeURIComponent(
    DEVICE_NAME,
  )}&type=${encodeURIComponent(DEVICE_TYPE)}`;

  const deviceInfoResp = http.get(deviceInfoUrl, {
    tags: { endpoint: "get_device_by_name_type" },
  });

  const deviceInfoOk = check(deviceInfoResp, {
    "get_device 200 or 404": (r) => r.status === 200 || r.status === 404,
  });
  if (!deviceInfoOk) {
    errorRate.add(1);
  }

  // ---- latest position for a device ----
  const lastPosResp = http.get(
    `${BASE}/device/position/last/${DEVICE_ID}`,
    {
      tags: { endpoint: "latest_position" },
    },
  );

  const lastPosOk = check(lastPosResp, {
    "latest_position 200 or 404": (r) =>
      r.status === 200 || r.status === 404,
  });
  if (!lastPosOk) {
    errorRate.add(1);
  }

  // ---- track movement (default 10s) ----
  const trackResp = http.get(
    `${BASE}/device/position/track/${DEVICE_ID}?sec=10`,
    {
      tags: { endpoint: "track_position" },
    },
  );

  const trackOk = check(trackResp, {
    "track_position 200": (r) => r.status === 200,
    "track_position json array": (r) => {
      try {
        return Array.isArray(r.json());
      } catch (_e) {
        return false;
      }
    },
  });
  if (!trackOk) {
    errorRate.add(1);
  }
}

/**
 * Run POST endpoints:
 * - POST /device/position/{device_id}
 *
 * This simulates a device sending a new position sample.
 */
export function runPostApiTesting() {
  const url = `${BASE}/device/position/${DEVICE_ID}`;

  // random-ish coords in [0, 10] within constraint.
  const x = Math.random() * 10;
  const y = Math.random() * 10;

  const payload = JSON.stringify({ x, y });

  const headers = {
    "Content-Type": "application/json",
  };

  const resp = http.post(url, payload, {
    headers,
    tags: { endpoint: "update_position" },
  });

  const ok = check(resp, {
    "update_position 201": (r) => r.status === 201,
  });
  if (!ok) {
    errorRate.add(1);
  }
}
