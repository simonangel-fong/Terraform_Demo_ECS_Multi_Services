# Terraform Demo: ECS Multi-services - AWS Infrastructure

[Back](../../README.md)

- [Terraform Demo: ECS Multi-services - AWS Infrastructure](#terraform-demo-ecs-multi-services---aws-infrastructure)
  - [Terraform - AWS](#terraform---aws)

---

## Terraform - AWS

```sh
cd aws

terraform init -backend-config=backend.config
terraform fmt && terraform validate

terraform plan
terraform apply -auto-approve

terraform destroy -auto-approve


# home
curl "https://demo-ecs-mul-svc.arguswatcher.net"
curl "https://demo-ecs-mul-svc.arguswatcher.net/health"
curl "https://demo-ecs-mul-svc.arguswatcher.net/health/db"
# list devices
curl "https://demo-ecs-mul-svc.arguswatcher.net/devices"
# get device
curl "https://demo-ecs-mul-svc.arguswatcher.net/devices/a5124a19-2725-4e07-9fdf-cb54a451204a"

# get telemetry:
curl "https://demo-ecs-mul-svc.arguswatcher.net/telemetry/a5124a19-2725-4e07-9fdf-cb54a451204a" -H "Content-Type: application/json" -H "X-api-key: dev-alpha"

# post telemetry:
curl -X POST "https://demo-ecs-mul-svc.arguswatcher.net/telemetry/a5124a19-2725-4e07-9fdf-cb54a451204a" ^
  -H "Content-Type: application/json" ^
  -H "X-api-key: dev-alpha" ^
  -d '{"x_coord": 123.456, "y_coord": 78.9, "device_time": "2025-11-17T18:31:56Z"}'
```
