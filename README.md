# Terraform Demo: ECS(Fargate) - Multiple Services

## Postgresql

```sh
cd app/pgdb

docker compose up -d --build
docker compose down -v
```

## FastAPI

```sh
cd app/fastapi

python -m venv .venv
python.exe -m pip install --upgrade pip

pip install fastapi "uvicorn[standard]" "SQLAlchemy[asyncio]" asyncpg pydantic python-dotenv pydantic-settings

pip freeze > requirements.txt

uvicorn app.main:app --reload
uvicorn app.main:app --host 0.0.0.0 --port 8000

# test
# Create
curl -X POST http://localhost:8000/trips -H "Content-Type: application/json" -d "{\"start_station\":\"Central station\"}"
# {"start_time":"2025-11-12T06:12:24.727736Z","start_station":"Central station","trip_id":3}

# List
curl http://localhost:8000/trips
# [{"start_time":"2025-11-12T05:35:05.386564Z","start_station":"Central station","trip_id":1},{"start_time":"2025-11-12T05:35:05.386564Z","start_station":"Arial station","trip_id":2}]

# Get one
curl http://localhost:8000/trips/1
# {"start_time":"2025-11-12T05:35:05.386564Z","start_station":"Central station","trip_id":1}

# Update
curl -X PUT http://localhost:8000/trips/1 -H "Content-Type: application/json" -d "{\"start_station\":\"Union Station\"}"
# {"start_time":"2025-11-12T06:08:46.060890Z","start_station":"Union Station","trip_id":1}

# Delete
curl -X DELETE http://localhost:8000/trips/1 -i
# HTTP/1.1 204 No Content
# date: Wed, 12 Nov 2025 06:00:21 GMT
# server: uvicorn
# content-type: application/json
```

---

## CI Testing

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
```
