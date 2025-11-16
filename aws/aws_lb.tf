# ##############################
# ALB SG
# ##############################
resource "aws_security_group" "sg_lb" {
  name        = "${var.project}-sg-lb"
  description = "ALB security group"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-lb-sg"
  }
}

# ##############################
# ALB
# ##############################
resource "aws_alb" "lb" {
  name               = "${var.project}-lb"
  load_balancer_type = "application"
  subnets            = [for subnet in aws_subnet.public : subnet.id]
  security_groups    = [aws_security_group.sg_lb.id]
}

# ##############################
# ALB listener
# ##############################
# Route traffic from the ALB to the target group
resource "aws_alb_listener" "lb_lsn" {
  load_balancer_arn = aws_alb.lb.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.lb_tg.arn
    type             = "forward"
  }
}

# ##############################
# ALB Target Group
# ##############################
resource "aws_alb_target_group" "lb_tg" {
  name        = "${var.project}-lb-tg"
  target_type = "ip"
  vpc_id      = aws_vpc.vpc.id
  port        = 8000
  protocol    = "HTTP"

  health_check {
    path                = "/healthz"
    matcher             = "200-399"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}
