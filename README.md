# Terraform Demo: ECS(Fargate) - Multiple Services

## Postgresql

```sh
cd app

docker build -t pgdb ./pgdb
docker compose down -v
docker compose up -d --build
docker tag pgdb simonangelfong/demo-ecs-svc-pgdb
docker push simonangelfong/demo-ecs-svc-pgdb

```

---

## FastAPI

```sh
cd app/fastapi

python -m venv .venv
python.exe -m pip install --upgrade pip

pip install fastapi "uvicorn[standard]" "SQLAlchemy[asyncio]" asyncpg pydantic python-dotenv pydantic-settings pytest pytest-asyncio httpx

pip freeze > requirements.txt

# uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --port 8000
python app/main.py
```

- Docker

```sh
cd app

docker build -t fastapi ./fastapi
docker compose down -v
docker compose up -d --build
docker tag fastapi simonangelfong/demo-ecs-svc-fastapi
docker push simonangelfong/demo-ecs-svc-fastapi
```


---

## CI Testing

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

### Smoke Testing

```sh
cd testing

# smoke testing
docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_smoke.html -v ./script:/scripts -v ./report:/report/ grafana/k6 run /scripts/test_smoke.js

# baseline(ramp-up) testing
docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_baseline.html -v ./script:/scripts -v ./report:/report/ grafana/k6 run /scripts/test_baseline.js

# spike testing
docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_spike.html -v ./script:/scripts -v ./report:/report/ grafana/k6 run /scripts/test_spike.js

# stress testing
docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_stress.html -v ./script:/scripts -v ./report:/report/ grafana/k6 run /scripts/test_stress.js

# soak testing
docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=/report/test_soak.html -v ./script:/scripts -v ./report:/report/ grafana/k6 run /scripts/test_soak.js

```




```sh
cd app

docker compose up -d --build
docker compose down -v

cd testing
docker build -t k6 .

# default test: 100rps, max 10 concurrency
docker run --rm --name k6_con --net=app_public_network -p 5665:5665 -e DOMAIN="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=report.html -v ./:/app k6 run script/test_read.js

docker run --rm --name k6_con --net=app_public_network -p 5665:5665 -e DOMAIN="http://fastapi:8000" -e RATE=500 -e PRE_VUS=2 -e MAX_VUS=50 -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=report.html -v ./:/app k6 run script/test_read.js

#      ✓ status is 200
#      ✓ json array

#      checks.........................: 100.00% ✓ 61842      ✗ 0
#      data_received..................: 9.5 MB  158 kB/s
#      data_sent......................: 2.3 MB  38 kB/s
#      dropped_iterations.............: 29079   483.15894/s
#      http_req_blocked...............: avg=6.54µs   min=730ns  med=5.28µs  max=1.93ms  p(90)=8.06µs   p(95)=9.14µs
#      http_req_connecting............: avg=459ns    min=0s     med=0s      max=1.17ms  p(90)=0s       p(95)=0s
#      http_req_duration..............: avg=95.75ms  min=8.07ms med=36.92ms max=1.13s   p(90)=241.18ms p(95)=330.62ms
#      ✓ { endpoint:trips_list }......: avg=95.75ms  min=8.07ms med=36.92ms max=1.13s   p(90)=241.18ms p(95)=330.62ms
#        { expected_response:true }...: avg=95.75ms  min=8.07ms med=36.92ms max=1.13s   p(90)=241.18ms p(95)=330.62ms
#      http_req_failed................: 0.00%   ✓ 0          ✗ 30921
#      ✓ { endpoint:trips_list }......: 0.00%   ✓ 0          ✗ 30921
#      http_req_receiving.............: avg=112.91µs min=9.2µs  med=96.72µs max=11.16ms p(90)=185.63µs p(95)=228.94µs
#      http_req_sending...............: avg=36.35µs  min=1.97µs med=23.74µs max=1.41ms  p(90)=79.14µs  p(95)=95.63µs
#      http_req_tls_handshaking.......: avg=0s       min=0s     med=0s      max=0s      p(90)=0s       p(95)=0s
#      http_req_waiting...............: avg=95.6ms   min=7.91ms med=36.73ms max=1.13s   p(90)=241.05ms p(95)=330.51ms
#      http_reqs......................: 30921   513.764489/s
#      iteration_duration.............: avg=95.78ms  min=8.86ms med=37.11ms max=1.13s   p(90)=241.05ms p(95)=330.74ms
#      iterations.....................: 30921   513.764489/s
#      vus............................: 50      min=48       max=50
#      vus_max........................: 50      min=50       max=50
# running (1m00.2s), 00/50 VUs, 30921 complete and 0 interrupted iterations
# read_high_rps ✓ [ 100% ] 00/50 VUs  1m0s  1000.00 iters/s

docker run --rm --name k6_con --net=app_public_network -p 5665:5665 -e DOMAIN="http://fastapi:8000" -e RATE=1000 -e PRE_VUS=60 -e MAX_VUS=200 -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=report.html -v ./:/app k6 run script/test_read.js


```

> dropped_iterations: 29079
> http_reqs: 30921
> iterations: 30921
> read_high_rps: 1000.00 iters/s
> duration: 1m0s
> Total iteration
> = read_high_rps * duration = 1000.00iter/s*60s = 60k iters
> = dropped_iterations+http_reqs = 29079 + 30921 = 60k iters
> http_reqs: actually execute
> dropped_iterations: API cannot keep up
> Effective RPS: http_reqs / 60s = 30,921 / 60s = 514 RPS, not 1000.
> iteration_duration: Average request/iteration duration ≈ 95.75 ms.
> Max iterations/sec ≈ VUs / avg_duration ≈ 50 / 0.09575 ≈ 522 iters/sec

---

## Test API Capacity

```sh
# explore capacity
docker run --rm --name k6_con --net=app_public_network -p 5665:5665 -e ENDPOINT="http://fastapi:8000" -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT=report.html -v ./:/app k6 run script/test_capacity.js
```

---

## Terraform - AWS

```sh
cd aws

terraform init -backend-config=backend.config
terraform fmt && terraform validate

terraform plan
terraform apply -auto-approve

```
