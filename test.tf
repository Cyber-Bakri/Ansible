# CloudWatch Log Group for Neptune Poller
resource "aws_cloudwatch_log_group" "neptune_poller_taskdef_log_group" {
  name              = "/ecs/${var.prefix}-neptune-poller-${lower(var.suffix)}"
  retention_in_days = 90
  tags              = var.tags
}

# Sumo Logic Poller Module
module "sumo_poller" {
  source  = "app.terraform.io/pgetech/mrad-sumo/aws"
  version = "0.0.11"

  aws_account         = local.environment_name
  aws_role            = var.aws_role

  http_source_name    = "${var.prefix}-neptune-poller-${local.environment_name}-${lower(var.suffix)}"
  log_group_name      = aws_cloudwatch_log_group.neptune_poller_taskdef_log_group.name
  filter_pattern      = ""
  disambiguator       = "${var.prefix}-graph-poller-${lower(var.suffix)}"

  tags = var.tags

  TFC_CONFIGURATION_VERSION_GIT_BRANCH = lower(local.environment_name)
}

# SSM Parameter for SQS Enable
resource "aws_ssm_parameter" "sqs_enable" {
  name  = "/${var.prefix}/poller-sqs-enable-${lower(local.environment_name)}-${lower(var.suffix)}"
  type  = "String"
  value = "TRUE"
  tags  = var.tags
  
  lifecycle {
    ignore_changes = [value, tags]
  }
}

# ECS Task Definition for Neptune Poller
resource "aws_ecs_task_definition" "neptune_poller_ecs_taskdef" {
  family               = "${var.prefix}-neptune-poller-${lower(var.suffix)}"
  execution_role_arn   = aws_iam_role.neptune_svc_taskdef_role.arn
  task_role_arn        = aws_iam_role.neptune_svc_taskdef_role.arn
  network_mode         = "awsvpc"
  cpu                  = 2048
  memory               = 4096
  requires_compatibilities = ["FARGATE"]

  container_definitions = templatefile("${path.module}/taskdefs/neptune_poller.json.tpl",
    {
      suffix                   = lower(var.suffix)
      node_env                 = var.node_env
      neptune_db_cluster_endpoint = aws_neptune_cluster.neptune_db_cluster.endpoint
      poller_log_group_taskdef = aws_cloudwatch_log_group.neptune_poller_taskdef_log_group.id
      account_number           = data.aws_caller_identity.current.account_id
      account_name             = lower(local.environment_name)
      health_check_host        = local.healthcheck_url
      source_hash              = local.graph_repo_commit
      prefix                   = var.prefix
    }
  )

  tags = var.tags

  depends_on = [
    aws_cloudwatch_log_group.neptune_poller_taskdef_log_group,
    aws_neptune_cluster.neptune_db_cluster
  ]
}

# Variable for poller IDs (add this to your variables.tf)
variable "poller_ids" {
  description = "List of poller IDs to create. Each ID will be used to create a separate poller service."
  type        = list(string)
  default     = ["1", "2", "3"]
}

# ECS Service for Neptune Poller - Multiple separate services
resource "aws_ecs_service" "neptune_poller_ecs_service" {
  count = length(var.poller_ids)
  
  name               = "${var.prefix}-neptune-poller-service-${var.poller_ids[count.index]}-${lower(var.suffix)}"
  cluster            = aws_ecs_cluster.neptune_service_ecs_cluster.arn
  task_definition    = aws_ecs_task_definition.neptune_poller_ecs_taskdef.arn
  launch_type        = "FARGATE"
  desired_count      = 1
  enable_execute_command = true

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 0

  network_configuration {
    assign_public_ip = false
    security_groups  = [aws_security_group.poller_service.id]
    subnets = [
      data.aws_subnet.mrad1.id,
      data.aws_subnet.mrad2.id,
      data.aws_subnet.mrad3.id,
    ]
  }

  propagate_tags = "SERVICE"
  tags           = var.tags

  depends_on = [
    aws_cloudwatch_log_group.neptune_poller_taskdef_log_group,
    aws_neptune_cluster.neptune_db_cluster
  ]
}

# Output to show the poller service details
output "neptune_poller_service_names" {
  description = "Names of all Neptune poller ECS services"
  value       = aws_ecs_service.neptune_poller_ecs_service[*].name
}

output "neptune_poller_service_ids" {
  description = "IDs of all Neptune poller ECS services"
  value       = aws_ecs_service.neptune_poller_ecs_service[*].id
}

output "neptune_poller_count" {
  description = "Number of separate poller services created"
  value       = length(var.poller_ids)
}

output "neptune_poller_ids" {
  description = "List of poller IDs used"
  value       = var.poller_ids
}

