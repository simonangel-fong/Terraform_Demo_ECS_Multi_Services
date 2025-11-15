# #################################
# CloudWatch: log group
# #################################
resource "aws_cloudwatch_log_group" "log_group_api" {
  name              = "/ecs/task/${var.project}-api"
  retention_in_days = 7
}

# ##############################
# Security Group
# ##############################
resource "aws_security_group" "sg_api" {
  name        = "${var.project}-sg-api"
  description = "App security group"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.sg_lb.id] # limit source: sg_lb
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-sg-api"
  }
}

# #################################
# ECS: Task Definition
# #################################
resource "aws_ecs_task_definition" "ecs_task_api" {
  family                   = "${var.project}-task-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn # enable exec

  container_definitions = file("./container/api.json")
}

# #################################
# ECS: Service
# #################################
resource "aws_ecs_service" "ecs_svc_api" {
  name    = "${var.project}-service-api"
  cluster = aws_ecs_cluster.ecs_cluster.id

  # task
  task_definition = aws_ecs_task_definition.ecs_task_api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  platform_version       = "LATEST"
  enable_execute_command = true

  # network
  network_configuration {
    security_groups  = [aws_security_group.sg_api.id]
    subnets          = [for subnet in aws_subnet.public : subnet.id]
    assign_public_ip = true # enable public ip
  }

  # lb
  load_balancer {
    target_group_arn = aws_alb_target_group.lb_tg.id
    container_name   = "fastapi"
    container_port   = 8000
  }

  depends_on = [aws_cloudwatch_log_group.log_group_api]
}
