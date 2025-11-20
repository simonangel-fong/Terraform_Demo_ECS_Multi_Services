import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

// Load device credentials once per k6 instance
const devices = new SharedArray("devices", () => {
  const raw = open("./cred.json"); // cred.json in same folder
  return JSON.parse(raw);
});

// Base URL (override with BASE_URL env var)
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  vus: 1,
  duration: "30s", // each VU will loop over all devices per iteration
};

export default function () {
  for (const device of devices) {
    const url = `${BASE_URL}/telemetry/latest/${device.device_uuid}`;

    const params = {
      headers: {
        "X-API-Key": device.api_key,
        "Content-Type": "application/json",
      },
    };

    const res = http.get(url, params);

    let body;
    if (res.status === 200) {
      // Avoid parsing when body is empty / not JSON
      try {
        body = res.json();
      } catch (e) {
        body = null;
      }
    }

    check(res, {
      "status is 200 or 404": (r) => r.status === 200 || r.status === 404,
      "if 200, body has matching device_uuid": () =>
        res.status === 200 && body
          ? body.device_uuid === device.device_uuid
          : true,
    });

    // Optional: debug logging, only when explicitly enabled
    if (__ENV.DEBUG === "1") {
      console.log(
        `[device=${device.alias || device.device_uuid}] status=${res.status}`
      );
    }

    // tiny pause between devices to avoid hammering
    sleep(0.2);
  }

  // small pause between iterations
  sleep(1);
}
