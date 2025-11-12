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

pip install fastapi "uvicorn[standard]"
```

---

## Terraform - AWS

```sh
cd aws

terraform init -backend-config=backend.config
```
