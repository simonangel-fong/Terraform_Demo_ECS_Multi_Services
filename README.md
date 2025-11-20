# Terraform Demo: ECS Multiple Services - Postgresql + FastAPI

- [App](./doc/app/app.md)
- [AWS](./doc/aws/aws.md)
- [Testing](./doc/testing/testing.md)

docker compose -f app/docker-compose.yaml down -v && docker compose -f app/docker-compose.yaml up -d --build



docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE_URL=http://nginx:8000 -e K6_WEB_DASHBOARD=true -v ./k6/script:/script -v ./k6/report:/report/ grafana/k6 run /script/test_smoke.js

docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE_URL=http://nginx:8000 -e K6_WEB_DASHBOARD=true -v ./k6/script:/script -v ./k6/report:/report/ grafana/k6 run /script/test_baseline.js

docker run --rm --name k6_smoke --net=app_public_network -p 5665:5665 -e BASE_URL=http://nginx:8000 -e K6_WEB_DASHBOARD=true -v ./k6/script:/script -v ./k6/report:/report/ grafana/k6 run /script/test_load.js

