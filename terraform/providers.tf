# Credentials come from your AWS CLI profile (run "aws configure" first).
# Never put access keys in this file.
provider "aws" {
  region = var.aws_region

  # These tags are added to every resource, so they are easy to find and clean up
  default_tags {
    tags = {
      Project   = "churn-prediction"
      ManagedBy = "terraform"
    }
  }
}
