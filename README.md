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

pip install fastapi "uvicorn[standard]" "SQLAlchemy[asyncio]" asyncpg pydantic python-dotenv

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


```

---

## Terraform - AWS

```sh
cd aws

terraform init -backend-config=backend.config
```
