# ##############################
# EFS SG
# ##############################
resource "aws_security_group" "efs_sg" {
  name        = "${var.project}-efs-sg"
  description = "Allow NFS access to EFS"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port   = 2049 # nfs port
    to_port     = 2049 # nfs port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ##############################
# EFS: File system
# ##############################
resource "aws_efs_file_system" "efs" {
  creation_token   = "${var.project}-efs"
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"
  encrypted        = true

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "${var.project}-efs"
  }
}


# ##############################
# EFS Mount Target
# ##############################
resource "aws_efs_mount_target" "efs_mt" {
  for_each = aws_subnet.subnets

  file_system_id  = aws_efs_file_system.efs.id
  subnet_id       = each.value.id
  security_groups = [aws_security_group.efs_sg.id]
}


# ##############################
# EFS Access Point
# ##############################
resource "aws_efs_access_point" "efs_ap" {
  file_system_id = aws_efs_file_system.efs.id

  posix_user {
    uid = 999
    gid = 999
  }

  root_directory {
    path = "/postgres"
    creation_info {
      owner_uid   = 999
      owner_gid   = 999
      permissions = "0770"
    }
  }

  tags = {
    Name = "${var.project}-efs-ap"
  }

  depends_on = [aws_vpc.vpc]
}

