# #################################
# CloudWatch: log group
# #################################
resource "aws_cloudwatch_log_group" "log_group_db" {
  name              = "/ecs/task/${var.project}-db"
  retention_in_days = 7
}

resource "aws_security_group" "sg_db" {
  name        = "${var.project}-db-sg"
  description = "Database security group"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.sg_api.id] # limit source: sg_api
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-sg-db"
  }
}

# #################################
# Cloud Map: allow access for db service
# #################################
# Create namespace within VPC
resource "aws_service_discovery_private_dns_namespace" "dns_ns_vpc" {
  name        = "${var.project}.local"
  description = "Private DNS namespace"
  vpc         = aws_vpc.vpc.id
}

# #################################
# Cloud Map: DB service
# This is what ECS will register tasks into
# #################################
# register service: db
resource "aws_service_discovery_service" "db" {
  name = "pgdb" # service name: pgdb.${var.project}.local

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.dns_ns_vpc.id # relate with dns namespace

    dns_records {
      type = "A"
      ttl  = 10
    }

    routing_policy = "WEIGHTED"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

# #################################
# ECS: Task Definition
# #################################
resource "aws_ecs_task_definition" "ecs_task_db" {
  family                   = "${var.project}-task-db"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 4096
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn # enable exec

  volume {
    name = "pgdata"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.efs.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.efs_ap.id
        iam             = "ENABLED"
      }
    }
  }

  container_definitions = file("./container/db.json")
}

# #################################
# ECS: Service
# #################################
resource "aws_ecs_service" "ecs_svc_db" {
  name    = "${var.project}-service-db"
  cluster = aws_ecs_cluster.ecs_cluster.id

  # task
  task_definition = aws_ecs_task_definition.ecs_task_db.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  platform_version       = "LATEST"
  enable_execute_command = true

  # network
  network_configuration {
    security_groups  = [aws_security_group.sg_db.id]
    subnets          = [for subnet in aws_subnet.private : subnet.id]
    assign_public_ip = false # disable public ip
  }

  # service discovery
  service_registries {
    registry_arn = aws_service_discovery_service.db.arn
  }

  depends_on = [aws_cloudwatch_log_group.log_group_db]
}
