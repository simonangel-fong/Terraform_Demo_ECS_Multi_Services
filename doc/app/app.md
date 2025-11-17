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

pip install fastapi "uvicorn[standard]" "SQLAlchemy[asyncio]" asyncpg pydantic python-dotenv pydantic-settings  pytest pytest-asyncio httpx uvloop

pip freeze > requirements.txt

# python app/main.py
uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Develop with Docker Compose

```sh
docker compose -f ./app/docker-compose.yaml down -v
docker compose -f ./app/docker-compose.yaml up -d --build

# home
curl http://localhost:8000/
# list devices
curl "http://localhost:8000/devices"
curl "http://localhost:8000/devices?limit=5&offset=0"

# get device:
curl "http://localhost:8000/devices/info?name=device-001&type=sensor"
# get latest position:
curl "http://localhost:8000/device/position/last/3"
# Update / append position & Track
curl -X POST "http://localhost:8000/device/position/3" `
  -H "Content-Type: application/json" `
  -d "{""x"": 4.5, ""y"": 7.2}"
curl "http://localhost:8000/device/position/track/3?sec=30"
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
