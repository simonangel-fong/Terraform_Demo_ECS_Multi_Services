# ##############################
# APP
# ##############################
variable "project" { default = "demo-ecs-mul-svc" }

# ##############################
# AWS
# ##############################
variable "aws_region" { type = string }

# ##############################
# Cloudflare
# ##############################
variable "cloudflare_api_token" { type = string }
variable "cloudflare_zone_id" { type = string }

# ##############################
# AWS VPC
# ##############################
variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "vpc_public_subnets" {
  type = map(object({
    subnet_name = string
    cidr_block  = string
    az_suffix   = string
  }))
  default = {
    public_subnet_1a = {
      subnet_name = "public_subnet_a"
      cidr_block  = "10.0.1.0/24"
      az_suffix   = "a"
    }
    public_subnet_1b = {
      subnet_name = "public_subnet_b"
      cidr_block  = "10.0.2.0/24"
      az_suffix   = "b"
    }
  }
}

variable "vpc_private_subnets" {
  type = map(object({
    subnet_name = string
    cidr_block  = string
    az_suffix   = string
  }))
  default = {
    public_subnet_1a = {
      subnet_name = "private_subnet_a"
      cidr_block  = "10.0.101.0/24"
      az_suffix   = "a"
    }
    public_subnet_1b = {
      subnet_name = "private_subnet_b"
      cidr_block  = "10.0.102.0/24"
      az_suffix   = "b"
    }
  }
}

variable "dns_domain" {
  default = "arguswatcher.net"
}
