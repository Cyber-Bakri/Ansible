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
