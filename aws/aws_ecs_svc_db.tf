# #################################
# IAM: ECS Task Execution Role
# #################################
# assume role
resource "aws_iam_role" "ecs_task_execution_role_db" {
  name               = "${var.project}-task-execution-role-db"
  assume_role_policy = data.aws_iam_policy_document.task_assume_policy.json

  tags = {
    Project = var.project
    Role    = "ecs-task-execution-role-db"
  }
}

# policy attachment: exec role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_db" {
  role       = aws_iam_role.ecs_task_execution_role_db.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# #################################
# IAM: ECS Task Role
# #################################
resource "aws_iam_role" "ecs_task_role_db" {
  name               = "${var.project}-task-role-db"
  assume_role_policy = data.aws_iam_policy_document.task_assume_policy.json

  tags = {
    Project = var.project
    Role    = "ecs-task-role-db"
  }
}

# EFS client policy
resource "aws_iam_policy" "efs_client_policy" {
  name = "${var.project}-efs-client-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:ClientRootAccess"
        ],
        Resource = aws_efs_access_point.efs_ap.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_efs_client_policy" {
  role       = aws_iam_role.ecs_task_role_db.name
  policy_arn = aws_iam_policy.efs_client_policy.arn
}

# ##############################
# NAT: allow DB access to Internet for pulling image
# ##############################
# Elastic IP
resource "aws_eip" "eip_nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project}-eip-nat"
  }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.eip_nat.id

  # 1st public subnet from the map
  subnet_id = values(aws_subnet.public)[0].id

  tags = {
    Name = "${var.project}-nat-gw"
  }

  depends_on = [aws_internet_gateway.igw]
}

# map the private route 0.0.0.0/0 via NAT
resource "aws_route" "private_to_nat" {
  route_table_id         = aws_default_route_table.default.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gw.id
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
# CloudWatch: log group
# #################################
resource "aws_cloudwatch_log_group" "log_group_db" {
  name              = "/ecs/task/${var.project}-db"
  retention_in_days = 7
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
# ECS: Task Definition
# #################################
resource "aws_ecs_task_definition" "ecs_task_db" {
  family                   = "${var.project}-task-db"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 4096
  execution_role_arn       = aws_iam_role.ecs_task_execution_role_db.arn
  task_role_arn            = aws_iam_role.ecs_task_role_db.arn # task role

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
  task_definition  = aws_ecs_task_definition.ecs_task_db.arn
  desired_count    = 1
  launch_type      = "FARGATE"
  platform_version = "LATEST"

  # network
  network_configuration {
    security_groups  = [aws_security_group.sg_db.id]
    subnets          = [for subnet in aws_subnet.private : subnet.id]
    assign_public_ip = false # disable public ip
  }

  # service connnect
  service_connect_configuration {
    enabled   = true
    namespace = "${var.project}.local"

    service {
      discovery_name = "pgdb" # how other services refer to it
      port_name      = "db"   # must match port name in db.json

      client_alias {
        port     = 5432
        dns_name = "pgdb" # what your clients will resolve
      }
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.log_group_db,
  ]
}
