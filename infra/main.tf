module "nlbman_lambda" {
  source  = "app.terraform.io/pgetech/lambda/aws//modules/lambda_s3_bucket"
  version = "0.1.1"

  function_name                = local.lambda_name
  description                  = "Manage Network Load Balancers"
  memory_size                  = "256"
  timeout                      = "900"
  runtime                      = "nodejs20.x"
  handler                      = "src/index.handler"
  tags                         = var.tags
  vpc_config_security_group_ids = [data.aws_security_group.lambda_sg.id]
  vpc_config_subnet_ids        = [data.aws_subnet.mrad1.id, data.aws_subnet.mrad2.id, data.aws_subnet.mrad3.id]
  role                         = aws_iam_role.lambda_role.arn

  # Lambda is pulled from an S3 bucket:
  s3_bucket = local.s3_bucket
  s3_key    = aws_s3_object.lambda_zip.key

  # NODE_ENV is one of dev, qa, or production
  environment_variables = {
    "kms_key_arn" : null,
    "variables" : {
      LOG_LEVEL                    = local.account_num == "990878119577" ? "DEBUG" : "INFO"
      NODE_ENV                     = local.node_env
      SUFFIX                       = local.suffix
      PREFIX                       = local.prefix
      SHORT_NAME                   = local.short_name
      AWS_LAMBDA_EXEC_WRAPPER      = "/opt/otel-handler"
      OTEL_TRACES_SAMPLER          = "always_on"
      OTEL_SERVICE_NAME            = local.lambda_name
      SUMO_OTLP_HTTP_ENDPOINT_URL  = local.sumologic_endpoint
      OTEL_RESOURCE_ATTRIBUTES     = "application=${local.short_name},deployment.environment=${local.suffix},cloud.account.id=${local.account_num}"
    }
  }

  layers = [
    local.sumo_layer_arn,
    data.aws_lambda_layer_version.cloud_utilities.arn
  ]
}

module "lambda_logs" {
  source  = "app.terraform.io/pgetech/cloudwatch/aws//modules/log-group"
  version = "0.1.2"
  name    = "/aws/lambda/${local.lambda_name}"
  tags    = var.tags
}

resource "aws_lambda_permission" "cloudwatch_event" {
  statement_id  = "${local.lambda_name}-cloudwatch"
  action        = "lambda:InvokeFunction"
  function_name = local.lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ssm_parameter_change.arn
}

# when the SSM parameter is updated, the Lambda will be triggered
resource "aws_cloudwatch_event_rule" "ssm_parameter_change" {
  name        = "${local.lambda_name}-ssm-trigger"
  description = "Triggers Lambda when SSM parameter changes"
  event_pattern = jsonencode({
    "source" : [
      "aws.ssm"
    ],
    "detail-type" : [
      "Parameter Store Change"
    ],
    "account" : [
      local.account_num
    ],
    "resources" : [
      "arn:aws:ssm:us-west-2:${local.account_num}:parameter/webcore/${var.suffix}/active-neptune-cluster"
    ],
    "detail" : {
      "operation" : [
        "Create",
        "Update",
        "Delete",
        "LabelParameterVersion"
      ]
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule = aws_cloudwatch_event_rule.ssm_parameter_change.name
  arn  = module.nlbman_lambda.lambda_arn
}

resource "aws_cloudwatch_event_target" "sns_notify" {
  rule = aws_cloudwatch_event_rule.ssm_parameter_change.name
  arn  = "arn:aws:sns:us-west-2:${local.account_num}:webcore_notify"
}

module "nlbman_sumo" {
  source  = "app.terraform.io/pgetech/mrad-sumo/aws"
  version = "0.0.11"

  http_source_name = "sumo-${local.lambda_name}"
  aws_account      = local.envname
  aws_role         = "MRAD Ops"
  tags             = var.tags
  filter_pattern   = ""
  log_group_name   = module.lambda_logs.cloudwatch_log_group_name

  # disambiguator below needs to be unique per-account, therefore include the Lambda short name
  disambiguator                      = local.lambda_name
  TFC_CONFIGURATION_VERSION_GIT_BRANCH = var.git_branch
}

# ==========================================
# Neptune Event Handling Resources
# ==========================================

# SNS Topic to receive Neptune event notifications
resource "aws_sns_topic" "engage_neptune_events_topic" {
  name = "engage_neptune_events_topic-${var.suffix}"
  tags = var.tags
}

# Neptune Event Subscription - monitors db_instance level events
resource "aws_neptune_event_subscription" "engage_neptune_events_sub" {
  name          = "engage-neptune-events-sub-${var.suffix}"
  sns_topic_arn = aws_sns_topic.engage_neptune_events_topic.arn

  source_type = "db-instance"
  
  event_categories = [
    "availability",
    "deletion",
    "failover"
  ]

  tags = var.tags
}

# SNS Topic Subscription - connects SNS topic to Lambda function (NLB Manager)
resource "aws_sns_topic_subscription" "engage_neptune_topic_nlblambda" {
  topic_arn = aws_sns_topic.engage_neptune_events_topic.arn
  protocol  = "lambda"
  endpoint  = module.nlbman_lambda.lambda_arn
}

# Lambda Permission - allows SNS to invoke Lambda function
resource "aws_lambda_permission" "allow_sns_invoke_engage_nlbman" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = local.lambda_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.engage_neptune_events_topic.arn
}

