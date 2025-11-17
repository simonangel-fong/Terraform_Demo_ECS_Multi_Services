# Terraform Demo: ECS Multiple Services - Postgresql + FastAPI

- [App](./doc/app/app.md)
- [AWS](./doc/aws/aws.md)
- [Testing](./doc/testing/testing.md)

Base resource: /telemetry

List telemetry (all or filtered)
GET /telemetry

List telemetry for a specific device
GET /telemetry/{device_id}

Ingest telemetry for a specific device
POST /telemetry/{device_id}

there is not such thing:
Ingest telemetry (multi-device batch or single)
POST /telemetry

the api is the communication between server and devices, batch job is management job handled by different method