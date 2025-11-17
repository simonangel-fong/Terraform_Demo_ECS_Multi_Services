## Pattern 1 – Modular monolith (single service, single DB)

- One API service (like your FastAPI app).
- One DB (often Postgres).
- Good module boundaries in code:

  - accounts
  - auth
  - billing
  - devices
  - telemetry
  - routers & models.

- Telemetry tables might be:

  - Heavily indexed/partitioned (like you already did).
  - Possibly in a different schema.

- Used by:
  - lots of early/mid-stage SaaS & IoT products.
- Pros:
  - simple to deploy, easy to refactor, easy to reason about.
- Cons:
  - everything scales together; at very high throughput, telemetry can dominate.

---

## Pattern 2 – Modular monolith + separate telemetry DB

- Still one service, but:

  - DB A: metadata/control plane
    - accounts, users, api_keys, subscriptions, plans, devices
  - DB B: telemetry / time series
    - device_telemetry, device_latest, maybe materialized views
    - a specialized store (TimescaleDB, ClickHouse, Influx, etc.), but can also just be a second Postgres cluster.

- Used by: systems where telemetry is heavy, but org is still small.
- Pros:
  - Telemetry load doesn’t affect transactional DB as much.
  - Still one codebase / service → simple operations.
- Cons:
  - Slightly more infra: second DB, backups, monitoring.

---

## Pattern 3 – Microservices

- Typical split:

  - Auth / Identity Service
  - users, api_keys
  - Billing / Subscription Service
  - subscriptions, plans
  - Device Registry Service
    - devices, device status, config
  - Telemetry Ingestion Service
    - write-only API for telemetry
    - writes to telemetry DB / Kafka / time-series
  - Analytics / Reporting Service
    - reads from warehouse or time-series store

- Each service has its own DB and communicates via:

  - HTTP/REST/GraphQL for control-plane actions.
  - Queues/streams (Kafka, Kinesis, SQS) for telemetry and events.

- Used by: big IoT platforms / big orgs with multiple teams.
- Pros:

  - Each service can scale and evolve independently.
  - Telemetry pipeline can be super specialized and tuned.
  - Fault isolation (telemetry spike doesn’t kill auth service).

- Cons:
  - Much higher complexity: deployment, observability, retries, versioning, contracts between services.
  - CI/CD, infra, debugging all become more involved.
  - Overkill for a single dev / small team at early stage.
