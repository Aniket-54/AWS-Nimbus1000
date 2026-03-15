variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "recruitment-assistant"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for resume storage"
  type        = string
  default     = "recruitment-resumes-bucket"
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for candidates"
  type        = string
  default     = "Candidates"
}
