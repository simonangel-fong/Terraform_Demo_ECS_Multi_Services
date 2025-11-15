# ##############################
# VPC
# ##############################
resource "aws_vpc" "vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project}-vpc"
  }
}

# ##############################
# Internet Gateway
# ##############################
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project}-igw"
  }
}

# ##############################
# Route Table
# ##############################
# rt: default, private
resource "aws_default_route_table" "default" {
  default_route_table_id = aws_vpc.vpc.default_route_table_id

  tags = {
    Name = "${var.project}-default-rt-private"
  }
}

# rt public
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project}-rt-public"
  }
}

# ##############################
# Subnet
# ##############################

# private subnet
resource "aws_subnet" "private" {
  for_each = var.vpc_private_subnets

  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = each.value.cidr_block
  availability_zone       = "${var.aws_region}${each.value.az_suffix}"
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.project}-${each.value.subnet_name}"
  }
}

# public subnet
resource "aws_subnet" "public" {
  for_each = var.vpc_public_subnets

  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = each.value.cidr_block
  availability_zone       = "${var.aws_region}${each.value.az_suffix}"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project}-${each.value.subnet_name}"
  }
}

# ##############################
# Route Table Associations
# ##############################
resource "aws_route_table_association" "default" {
  for_each       = var.vpc_public_subnets
  subnet_id      = aws_subnet.public[each.key].id
  route_table_id = aws_default_route_table.default.id
}

resource "aws_route_table_association" "public" {
  for_each       = var.vpc_private_subnets
  subnet_id      = aws_subnet.private[each.key].id
  route_table_id = aws_route_table.public.id
}

# # ##############################
# # Security Group
# # ##############################
# resource "aws_security_group" "sg_app" {
#   name        = "${var.project}-sg-app"
#   description = "App security group"
#   vpc_id      = aws_vpc.vpc.id

#   ingress {
#     from_port       = 8000
#     to_port         = 8000
#     protocol        = "tcp"
#     security_groups = [aws_security_group.sg_lb.id] # limit source: sg_lb
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = {
#     Name = "${var.project}-sg-app"
#   }
# }
