resource "aws_neptune_subnet_group" "neptune_subnet_group" {
  name       = "${var.prefix}-db-${lower(var.suffix)}"
  description = "Subnet group for Engage Neptune DB"
  subnet_ids = [
    data.aws_subnet.ared1.id,
    data.aws_subnet.ared2.id,
    data.aws_subnet.ared3.id,
  ]

  tags = var.tags
}

resource "aws_neptune_cluster" "neptune_db_cluster" {
  cluster_identifier                   = "${var.prefix}-neptune-${lower(var.suffix)}"
  storage_encrypted                    = true
  kms_key_arn                         = aws_kms_key.neptune_db.arn
  neptune_subnet_group_name           = aws_neptune_subnet_group.neptune_subnet_group.id
  vpc_security_group_ids              = [aws_security_group.db_security_group.id]
  port                                = var.neptune_db_cluster_port
  skip_final_snapshot                 = true
  backup_retention_period             = local.neptune_backup_retention
  neptune_cluster_parameter_group_name = aws_neptune_cluster_parameter_group.neptune_db_cluster.name
  copy_tags_to_snapshot               = true
  enable_cloudwatch_logs_exports      = ["audit", "slowquery"]
  preferred_backup_window             = "00:30-11:30"  # time is in UTC
  engine_version                      = "1.3.4.0"      # engage-4705
  allow_major_version_upgrade         = true
  iam_database_authentication_enabled = true
  
  # Specify availability zones
  availability_zones = [
    data.aws_subnet.ared1.availability_zone,
    data.aws_subnet.ared2.availability_zone,
    data.aws_subnet.ared3.availability_zone,
  ]

  tags = var.tags
}

resource "aws_neptune_cluster_parameter_group" "neptune_db_cluster" {
  family      = "neptune1.3"
  name        = "${var.prefix}-neptune-cluster-${lower(var.suffix)}"
  description = "Engage Neptune cluster parameter group"
  tags        = var.tags
  
  parameter {
    name  = "neptune_enable_audit_log"
    value = 1
  }
  
  parameter {
    name  = "neptune_enable_slow_query_log"
    value = "info"
  }
}

resource "aws_neptune_cluster_instance" "neptune_db_instance" {
  count                        = local.neptune_instance_count
  cluster_identifier           = aws_neptune_cluster.neptune_db_cluster.id
  identifier                   = "${var.prefix}${var.suffix}${format("%02s", count.index)}"
  instance_class               = local.neptune_db_instance_class
  promotion_tier               = count.index + 1
  neptune_parameter_group_name = aws_neptune_parameter_group.neptune_db_instance.name
  
  # Explicitly set availability zone to ensure each instance is in a separate AZ
  availability_zone = element([
    data.aws_subnet.ared1.availability_zone,
    data.aws_subnet.ared2.availability_zone,
    data.aws_subnet.ared3.availability_zone
  ], count.index)

  tags = var.tags

  depends_on = [
    aws_neptune_cluster.neptune_db_cluster
  ]
}

resource "aws_neptune_parameter_group" "neptune_db_instance" {
  family = "neptune1.3"
  name   = "${var.prefix}-neptune-instance-${lower(var.suffix)}"
  tags   = var.tags
  
  parameter {
    name  = "neptune_result_cache"
    value = "1"
  }
}
