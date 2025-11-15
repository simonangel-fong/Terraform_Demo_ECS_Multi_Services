# Terraform Demo: ECS Multi-services - Testing

[Back](../../README.md)

- [Terraform Demo: ECS Multi-services - Testing](#terraform-demo-ecs-multi-services---testing)
  - [CI Testing Plan](#ci-testing-plan)
  - [Local CI Testing](#local-ci-testing)
  - [Cloud Deployment Testing](#cloud-deployment-testing)

---

## CI Testing Plan

- `Smoke Test`

  - **Goal**: Quickly verify that key endpoints and the test setup work before heavier tests.
  - **Load**: Very low RPS (e.g., 5–20) for about 1 minute.
  - **Focus Metrics**:
    - HTTP status (mainly 200s)
    - Basic correctness (JSON shape, key fields)
    - Connectivity and basic latency (nothing obviously broken)

- `Baseline / Ramp-up Test`

  - **Goal**: Understand normal, steady-state performance at expected real-world load.
  - **Load**: Gradual ramp up to target RPS over 5–15 minutes.
  - **Focus Metrics**:
    - RPS
    - p50 / p95 / p99 latency
    - Error rate
    - **Infrastructure metrics**: CPU, memory, DB connections

- `Spike Test`

  - **Goal**: See how the system behaves under sudden, short bursts of high traffic.
  - **Load**: Short bursts (2–5 minutes) of much higher RPS than normal.
  - **Focus Metrics**:
    - Error rate and timeouts during the spike
    - Latency spikes and recovery time after the spike
    - Autoscaling or protective mechanisms (if any) triggering correctly

- `Stress Test`

  - **Goal**: Find the system’s breaking point and how it fails when overloaded.
  - **Load**: Gradually increase load until performance clearly degrades or resources saturate.
  - **Focus Metrics**:
    - Maximum sustainable RPS before degradation
    - Error rate and failure patterns
    - Resource limits: CPU, memory, DB connection pool, threads/workers

- `Soak (Endurance) Test`

  - **Goal**: Detect long-term issues like memory leaks or slow degradation.
  - **Load**: Moderate, realistic load for a long period (1–4+ hours).
  - **Focus Metrics**:
    - Memory usage over time (no steady creep)
    - Open file descriptors / connections (no leaks)
    - Error rate stability
    - Latency drift or performance degradation over time

- Typical order of execution: `Smoke` → `Baseline/Ramp-up` → `Spike` → `Stress` → `Soak`.

---

## Local CI Testing

```sh
# start service
docker compose -f app/docker-compose.yaml up -d --build

# smoke testing
docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_smoke.html -v ./testing/script:/script -v ./testing/report:/report/ grafana/k6 run /script/test_smoke.js

# baseline(ramp-up) testing
docker run --rm --name k6_baseline --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_baseline.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_baseline.js

# spike testing
docker run --rm --name k6_spike --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_spike.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_spike.js

# stress testing
docker run --rm --name k6_stress --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_stress.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_stress.js

# soak testing
docker run --rm --name k6_soak --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_soak.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_soak.js
```

---

## Cloud Deployment Testing

```sh
# smoke testing
docker run --rm --name k6_smoke -p 5665:5665 -e BASE="https://demo-ecs-mul-svc.arguswatcher.net" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/aws_test_smoke.html -v ./testing/script:/script -v ./testing/report:/report/ grafana/k6 run /script/test_smoke.js

# baseline(ramp-up) testing
docker run --rm --name k6_baseline -p 5665:5665 -e BASE="https://demo-ecs-mul-svc.arguswatcher.net" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_baseline.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_baseline.js

# spike testing
docker run --rm --name k6_spike -p 5665:5665 -e BASE="https://demo-ecs-mul-svc.arguswatcher.net" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_spike.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_spike.js

# stress testing
docker run --rm --name k6_stress -p 5665:5665 -e BASE="https://demo-ecs-mul-svc.arguswatcher.net" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_stress.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_stress.js

# soak testing
docker run --rm --name k6_soak -p 5665:5665 -e BASE="https://demo-ecs-mul-svc.arguswatcher.net" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_soak.html -v ./testing/script:/scripts -v ./testing/report:/report/ grafana/k6 run /scripts/test_soak.js

```
