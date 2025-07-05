provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "sigmatekclassstate"          # The name of your S3 bucket
    key    = "terraform.tfstate"           # Path to store the state file within the bucket
    region = "us-east-1"                   # Your AWS region (change as needed)
    encrypt = true                         # Enable encryption of state file
    # dynamodb_table = "terraform-locks"     # DynamoDB table name for state locking (create this table if not already)
  }
}