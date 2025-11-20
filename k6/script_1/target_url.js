import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

// ==============================
// helpers
// ==============================

export const errorRate = new Rate("errors");

/**
 * Record the result of a check into the global error rate.
 * Pass `true` for success, `false` for failure.
 */
function recordError(ok) {
  errorRate.add(ok ? 0 : 1);
}

/**
 * Safely parse JSON, returning null on failure.
 *
 * @param {import("k6/http").Response} resp
 * @returns {any | null}
 */
function safeJson(resp) {
  try {
    return resp.json();
  } catch (_e) {
    return null;
  }
}

function parseNumberEnv(name, defaultValue) {
  const raw = __ENV[name];
  if (raw === undefined) return defaultValue;
  const n = Number(raw);
  return Number.isNaN(n) ? defaultValue : n;
}

// ==============================
// Environment configuration
// ==============================

export const BASE = __ENV.BASE || "http://localhost:8000";
export const DEVICE_UUID =
  __ENV.DEVICE_UUID || "a5124a19-2725-4e07-9fdf-cb54a451204a";
export const DEVICE_API_KEY = __ENV.DEVICE_API_KEY || "dev-alpha";

export const X_BOUNDARY = parseNumberEnv("X_BOUNDARY", 10);
export const Y_BOUNDARY = parseNumberEnv("Y_BOUNDARY", 10);

// ==============================
// GET Home - GET /
// ==============================
export function getHome() {
  const homeResp = http.get(`${BASE}/`, {
    tags: { endpoint: "home" },
  });

  const homeOk = check(homeResp, {
    "home 200": (r) => r.status === 200,
  });

  recordError(homeOk);
}

// ==============================
// GET Health - GET /health, /health/db
// ==============================

export function getHealth() {
  const healthResp = http.get(`${BASE}/health`, {
    tags: { endpoint: "health" },
  });

  const healthOk = check(healthResp, {
    "health 200": (r) => r.status === 200,
  });
  recordError(healthOk);

  const healthDbResp = http.get(`${BASE}/health/db`, {
    tags: { endpoint: "health_db" },
  });

  const healthDbOk = check(healthDbResp, {
    "health_db 200": (r) => r.status === 200,
  });
  recordError(healthDbOk);
}

// ==============================
// GET devices - GET /devices, /devices/{uuid}
// ==============================

export function getDevices() {
  const listResp = http.get(`${BASE}/devices`, {
    tags: { endpoint: "devices_get_all" },
  });

  const listOk = check(listResp, {
    "devices_get_all 200": (r) => r.status === 200,
    "devices_get_all json array": (r) => {
      const body = safeJson(r);
      return Array.isArray(body);
    },
  });
  recordError(listOk);

  const deviceDetailResp = http.get(`${BASE}/devices/${DEVICE_UUID}`, {
    tags: { endpoint: "device_get_by_uuid" },
  });

  const deviceDetailOk = check(deviceDetailResp, {
    "device_get_by_uuid 200 or": (r) => r.status === 200,
  });
  recordError(deviceDetailOk);
}

// ==============================
// GET telemetry - GET /telemetry/{device_uuid}
// ==============================

export function getTelemetry() {
  const telemetryUrl = `${BASE}/telemetry/${DEVICE_UUID}`;
  const telemetryHeaders = {
    "X-API-Key": DEVICE_API_KEY,
  };

  const telemetryResp = http.get(telemetryUrl, {
    headers: telemetryHeaders,
    tags: { endpoint: "telemetry_get" },
  });

  const telemetryOk = check(telemetryResp, {
    "telemetry_get 200": (r) => r.status === 200 || r.status === 404,
    "telemetry_get json array when 200": (r) => {
      if (r.status !== 200) return true;
      const body = safeJson(r);
      return Array.isArray(body);
    },
  });
  recordError(telemetryOk);
}

// ==============================
// POST telemetry - POST /telemetry/{device_uuid}
// ==============================

export function postTelemetry() {
  const url = `${BASE}/telemetry/${DEVICE_UUID}`;

  const x_coord = Math.random() * X_BOUNDARY;
  const y_coord = Math.random() * Y_BOUNDARY;

  const payload = JSON.stringify({
    x_coord,
    y_coord,
    device_time: new Date().toISOString(),
  });

  const headers = {
    "Content-Type": "application/json",
    "X-API-Key": DEVICE_API_KEY,
  };

  const resp = http.post(url, payload, {
    headers,
    tags: { endpoint: "telemetry_post" },
  });

  const ok = check(resp, {
    "telemetry_post 201": (r) => r.status === 201,
  });
  recordError(ok);
}
