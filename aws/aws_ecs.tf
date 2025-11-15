# ##############################
# IAM: ECS Task execution role
# ##############################
# assume policy
data "aws_iam_policy_document" "task_assume_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}


# #################################
# ECS: Cluster
# #################################
# cluster
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "${var.project}-cluster"
}

# #################################
# ECS: Capacity Provider
# #################################
resource "aws_ecs_cluster_capacity_providers" "ecs_cap" {
  cluster_name       = aws_ecs_cluster.ecs_cluster.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    base              = 1 # keep at least 1 on on-demand
    weight            = 1
  }

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 3 # ~75% of the remainder goes to spot
  }
}
