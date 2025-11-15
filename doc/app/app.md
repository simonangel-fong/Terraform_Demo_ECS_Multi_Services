## Terraform Demo: ECS Multi-services - Application

[Back](../../README.md)

- [Terraform Demo: ECS Multi-services - Application](#terraform-demo-ecs-multi-services---application)
- [Postgresql](#postgresql)
  - [!Database design](#database-design)
  - [Develop with Docker](#develop-with-docker)
  - [Push to DockerHub](#push-to-dockerhub)
  - [Push to ECR](#push-to-ecr)
- [FastAPI](#fastapi)
  - [Create Project Env](#create-project-env)
  - [Develop with Docker](#develop-with-docker-1)
  - [Push to DockerHub](#push-to-dockerhub-1)
  - [Push to ECR](#push-to-ecr-1)

---

## Postgresql

### !Database design

!Table

### Develop with Docker

```sh
cd app

docker build -t pgdb ./pgdb
docker run --name pgdb -p 5432:5432 pgdb
```

### Push to DockerHub

```sh
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
docker tag demo-ecs-multi-svc/db:latest 099139718958.dkr.ecr.ca-central-1.amazonaws.com/demo-ecs-multi-svc/db:latest

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

pip freeze > requirements.txt

# uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --port 8000
python app/main.py
```

### Develop with Docker

- Docker

```sh
cd app

# build image
docker build -t fastapi ./fastapi
dcoker run --name api -p 8000:8000 fastapi
```

---

### Push to DockerHub

- DockerHub

```sh
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
