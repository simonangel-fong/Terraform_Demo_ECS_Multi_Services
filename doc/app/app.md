## Terraform Demo: ECS Multi-services - Application

[Back](../../README.md)

- [Terraform Demo: ECS Multi-services - Application](#terraform-demo-ecs-multi-services---application)
- [Postgresql](#postgresql)
  - [!Database design](#database-design)
  - [Develop with Docker Compose](#develop-with-docker-compose)
  - [Push to DockerHub](#push-to-dockerhub)
  - [Push to ECR](#push-to-ecr)
- [FastAPI](#fastapi)
  - [Create Project Env](#create-project-env)
  - [Unit Test](#unit-test)
  - [Develop with Docker Compose](#develop-with-docker-compose-1)
  - [Push to DockerHub](#push-to-dockerhub-1)
  - [Push to ECR](#push-to-ecr-1)

---

## Postgresql

### !Database design

!Table

```sh
# custom config
postgres -c config_file=/config/postgresql.dev.conf

# load sample data
docker exec -it pgdb psql -U postgres -d app_db -f /script/01_stress_seed.sql
```

### Develop with Docker Compose

```sh
docker compose -f ./app/docker-compose.yaml down -v
docker compose -f ./app/docker-compose.yaml up -d --build
```

### Push to DockerHub

```sh
docker build -t pgdb ./app/pgdb
docker tag pgdb simonangelfong/demo-ecs-svc-pgdb
docker push simonangelfong/demo-ecs-svc-pgdb
```

### Push to ECR

- Create ECR private repo

```sh
# aws ecr delete-repository --repository-name demo-ecs-multi-svc/db --region ca-central-1
aws ecr create-repository --repository-name demo-ecs-multi-svc/db --region ca-central-1

# confirm
aws ecr describe-repositories
```

- Authenticate and push

```sh
# authenticate your Docker client to ECR.
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin 099139718958.dkr.ecr.ca-central-1.amazonaws.com
# Login Succeeded

# Build your Docker image
docker build -t demo-ecs-multi-svc/db ./app/pgdb

# tag your image
docker tag pgdb:latest 099139718958.dkr.ecr.ca-central-1.amazonaws.com/demo-ecs-multi-svc/db:latest

# push image to repository
docker push 099139718958.dkr.ecr.ca-central-1.amazonaws.com/demo-ecs-multi-svc/db:latest

# confirm
aws ecr describe-images --repository-name demo-ecs-multi-svc/db
```

---

## FastAPI

### Create Project Env

```sh
cd app/fastapi

python -m venv .venv
python.exe -m pip install --upgrade pip

pip install fastapi "uvicorn[standard]" "SQLAlchemy[asyncio]" asyncpg pydantic python-dotenv pydantic-settings pytest pytest-asyncio httpx

pip install uvloop
pip freeze > requirements.txt

# python app/main.py
uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Unit Test

```sh
cd app/fastapi

pip install pytest
```

---

### Develop with Docker Compose

```sh
docker compose -f ./app/docker-compose.yaml down -v
docker compose -f ./app/docker-compose.yaml up -d --build

# home
curl http://localhost:8000/
# {"service":"iot-device-management-api","status":"ok","environment":"dev","debug":true,"docs":{"openapi":"/openapi.json","swagger_ui":"/docs","redoc":"/redoc"}}

# health
curl http://localhost:8000/health
# {"status":"ok"}
curl http://localhost:8000/health/db
# {"database":"reachable"}

# list devices
curl "http://localhost:8000/devices"
# [{"name":"dev-alpha","device_uuid":"a5124a19-2725-4e07-9fdf-cb54a451204a","tracking_enabled":true,"created_at":"2025-11-18T15:57:03.400758Z","updated_at":"2025-11-18T15:57:03.400758Z"},{"name":"dev-bravo","device_uuid":"35dec641-554b-446f-9092-6652cb6fe3c0","tracking_enabled":true,"created_at":"2025-11-18T15:57:03.400758Z","updated_at":"2025-11-18T15:57:03.400758Z"},{"name":"dev-charlie","device_uuid":"d5a7fe62-28fb-49d9-906b-abed453d1cd4","tracking_enabled":false,"created_at":"2025-11-18T15:57:03.400758Z","updated_at":"2025-11-18T15:57:03.400758Z"}]
curl "http://localhost:8000/devices/a5124a19-2725-4e07-9fdf-cb54a451204a"
# {"name":"dev-alpha","device_uuid":"a5124a19-2725-4e07-9fdf-cb54a451204a","tracking_enabled":true,"created_at":"2025-11-18T15:57:03.400758Z","updated_at":"2025-11-18T15:57:03.400758Z"}

# get telemetry:
curl "http://localhost:8000/telemetry/a5124a19-2725-4e07-9fdf-cb54a451204a" -H "Content-Type: application/json" -H "X-api-key: dev-alpha"
# [
#   {"x_coord":123.456,"y_coord":78.9,"recorded_at":"2025-11-18T16:14:25.649239Z","device_time":"2025-11-17T12:34:56Z"},
#   {"x_coord":1763581.363409146,"y_coord":1763681.363409146,"recorded_at":"2025-11-18T15:56:03.409146Z","device_time":"2025-11-18T15:55:53.409146Z"},
#   {"x_coord":1763581.243409146,"y_coord":1763681.243409146,"recorded_at":"2025-11-18T15:54:03.409146Z","device_time":"2025-11-18T15:53:53.409146Z"},
#   {"x_coord":1763581.123409146,"y_coord":1763681.123409146,"recorded_at":"2025-11-18T15:52:03.409146Z","device_time":"2025-11-18T15:51:53.409146Z"}
# ]

curl -X POST "http://localhost:8000/telemetry/a5124a19-2725-4e07-9fdf-cb54a451204a" ^
  -H "Content-Type: application/json" ^
  -H "X-api-key: dev-alpha" ^
  -d '{"x_coord": 123.456, "y_coord": 78.9, "device_time": "2025-11-17T12:34:56Z"}'
```

---

### Push to DockerHub

- DockerHub

```sh
docker build -t fastapi ./app/fastapi
# tag
docker tag fastapi simonangelfong/demo-ecs-svc-fastapi
# push to docker
docker push simonangelfong/demo-ecs-svc-fastapi
```

---

### Push to ECR

- Create ECR private repo

```sh
# aws ecr delete-repository --repository-name demo-ecs-multi-svc/api --region ca-central-1
aws ecr create-repository --repository-name demo-ecs-multi-svc/api --region ca-central-1

# confirm
aws ecr describe-repositories
```

- Authenticate and push

```sh
# authenticate your Docker client to ECR.
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin 099139718958.dkr.ecr.ca-central-1.amazonaws.com
# Login Succeeded

# Build your Docker image
docker build -t demo-ecs-multi-svc/api ./app/fastapi

# tag your image
docker tag demo-ecs-multi-svc/api:latest 099139718958.dkr.ecr.ca-central-1.amazonaws.com/demo-ecs-multi-svc/api:latest

# push image to repository
docker push 099139718958.dkr.ecr.ca-central-1.amazonaws.com/demo-ecs-multi-svc/api:latest

# confirm
aws ecr describe-images --repository-name demo-ecs-multi-svc/api
```

---
