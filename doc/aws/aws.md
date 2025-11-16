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
curl https://demo-ecs-mul-svc.arguswatcher.net/
# list devices
curl "https://demo-ecs-mul-svc.arguswatcher.net/devices"
curl "https://demo-ecs-mul-svc.arguswatcher.net/devices?limit=5&offset=0"

# get device:
curl "https://demo-ecs-mul-svc.arguswatcher.net/devices/info?name=device-001&device_type=sensor"
# get latest position:
curl "https://demo-ecs-mul-svc.arguswatcher.net/device/position/last/3"
# Update / append position & Track
curl -X POST "http://demo-ecs-mul-svc.arguswatcher.net/device/position/3" `
  -H "Content-Type: application/json" `
  -d "{""x"": 4.5, ""y"": 7.2}"
curl "https://demo-ecs-mul-svc.arguswatcher.net/device/position/track/3?sec=30"
```
