The webcore infrastructure is still referencing outdated Terraform modules.

The viewer module is using the old s3web/aws module (v0.0.33) and should be updated to v0.1.9.

The CodePipeline webhook module currently referenced at
app.terraform.io/pgetech/codepipeline/aws//modules/codepipeline_webhook
is deprecated and has been replaced by
app.terraform.io/pgetech/codepipeline_internal/aws//modules/gh_webhook.

Updating these module sources will align the configuration with the currently supported versions and prevent future compatibility issues.
