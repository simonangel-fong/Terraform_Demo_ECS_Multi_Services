// target_url.js
import { checkGet, checkPost, buildTelemetryPayload } from "./common.js";


// ==============================
// Root
// ==============================
export function getHome({ base_url }) {
  return checkGet({
    url: `${base_url}/`,
    endpoint: "home",
  });
}

// ==============================
// Health check: app
// ==============================
export function getHealth({ base_url }) {
  return checkGet({
    url: `${base_url}/health`,
    endpoint: "health",
  });
}

// ==============================
// Health check: db
// ==============================
export function getHealthDB({ base_url }) {
  return checkGet({
    url: `${base_url}/health/db`,
    endpoint: "health_db",
  });
}

// ==============================
// Get /devices
// ==============================
export function getDevices({ base_url }) {
  return checkGet({
    url: `${base_url}/devices`,
    endpoint: "devices_get_all",
  });
}

// ========================================
// Get /telemetry/latest/{device_uuid}
// ========================================
export function getTelemetryLatest({ base_url, device }) {
  return checkGet({
    url: `${base_url}/telemetry/latest/${device.device_uuid}`,
    headers: { "X-API-Key": device.api_key },
    endpoint: "telemetry_get_latest",
    expectedStatuses: [200, 404],
  });
}

// ========================================
// POST /telemetry/{device_uuid}
// ========================================
export function postTelemetry({ base_url, device }) {
  const url = `${base_url}/telemetry/${device.device_uuid}`;
  const body = buildTelemetryPayload();

  return checkPost({
    url,
    endpoint: "telemetry_post",
    body,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": device.api_key,
    },
    expectedStatuses: [201],
  });
}

