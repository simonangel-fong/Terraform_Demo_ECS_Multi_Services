## Terraform Demo: ECS Multi-services - AWS Infrastructure

[Back](./README.md)

- [Terraform Demo: ECS Multi-services - AWS Infrastructure](#terraform-demo-ecs-multi-services---aws-infrastructure)
- [Terraform - AWS](#terraform---aws)

## Terraform - AWS

```sh
cd aws

terraform init -backend-config=backend.config
terraform fmt && terraform validate

terraform plan
terraform apply -auto-approve

terraform destroy -auto-approve

```
