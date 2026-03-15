terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket for Resume Storage
resource "aws_s3_bucket" "resume_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name        = "Recruitment Resume Storage"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "resume_bucket_versioning" {
  bucket = aws_s3_bucket.resume_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "resume_bucket_encryption" {
  bucket = aws_s3_bucket.resume_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Event Notification for Lambda Trigger
resource "aws_s3_bucket_notification" "resume_upload_notification" {
  bucket = aws_s3_bucket.resume_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.batch_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "resumes/"
    filter_suffix       = ".pdf"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

# DynamoDB Table for Candidate Data
resource "aws_dynamodb_table" "candidates" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "candidate_id"

  attribute {
    name = "candidate_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  attribute {
    name = "upload_timestamp"
    type = "S"
  }

  global_secondary_index {
    name            = "EmailIndex"
    hash_key        = "email"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "TimestampIndex"
    hash_key        = "upload_timestamp"
    projection_type = "ALL"
  }

  tags = {
    Name        = "Candidate Database"
    Environment = var.environment
  }
}

# IAM Role for Lambda Functions
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.resume_bucket.arn,
          "${aws_s3_bucket.resume_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          aws_dynamodb_table.candidates.arn,
          "${aws_dynamodb_table.candidates.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "textract:DetectDocumentText",
          "textract:AnalyzeDocument"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function - Upload Handler
resource "aws_lambda_function" "upload_handler" {
  filename      = "lambda_packages/upload_handler.zip"
  function_name = "${var.project_name}-upload-handler"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "backend.api.upload_resume_lambda.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      S3_BUCKET_NAME      = aws_s3_bucket.resume_bucket.id
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.candidates.name
      AWS_REGION          = var.aws_region
      TEXTRACT_ENABLED    = "true"
    }
  }

  tags = {
    Name = "Resume Upload Handler"
  }
}

# Lambda Function - Batch Processor
resource "aws_lambda_function" "batch_processor" {
  filename      = "lambda_packages/batch_processor.zip"
  function_name = "${var.project_name}-batch-processor"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "backend.api.batch_upload_lambda.lambda_handler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 1024

  environment {
    variables = {
      S3_BUCKET_NAME      = aws_s3_bucket.resume_bucket.id
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.candidates.name
      AWS_REGION          = var.aws_region
      TEXTRACT_ENABLED    = "true"
    }
  }

  tags = {
    Name = "Batch Resume Processor"
  }
}

# Lambda Function - Search Handler
resource "aws_lambda_function" "search_handler" {
  filename      = "lambda_packages/search_handler.zip"
  function_name = "${var.project_name}-search-handler"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "backend.api.search_candidates_lambda.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 512

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.candidates.name
      AWS_REGION          = var.aws_region
      USE_DYNAMODB        = "true"
    }
  }

  tags = {
    Name = "Candidate Search Handler"
  }
}

# Lambda Permission for S3 to invoke batch processor
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.batch_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.resume_bucket.arn
}

# API Gateway
resource "aws_api_gateway_rest_api" "recruitment_api" {
  name        = "${var.project_name}-api"
  description = "Recruitment Assistant API"

  binary_media_types = ["application/pdf", "multipart/form-data"]
}

# API Gateway Resource - Upload
resource "aws_api_gateway_resource" "upload" {
  rest_api_id = aws_api_gateway_rest_api.recruitment_api.id
  parent_id   = aws_api_gateway_rest_api.recruitment_api.root_resource_id
  path_part   = "upload"
}

# API Gateway Method - POST /upload
resource "aws_api_gateway_method" "upload_post" {
  rest_api_id   = aws_api_gateway_rest_api.recruitment_api.id
  resource_id   = aws_api_gateway_resource.upload.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration - Upload Lambda
resource "aws_api_gateway_integration" "upload_lambda" {
  rest_api_id = aws_api_gateway_rest_api.recruitment_api.id
  resource_id = aws_api_gateway_resource.upload.id
  http_method = aws_api_gateway_method.upload_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_handler.invoke_arn
}

# API Gateway Resource - Search
resource "aws_api_gateway_resource" "search" {
  rest_api_id = aws_api_gateway_rest_api.recruitment_api.id
  parent_id   = aws_api_gateway_rest_api.recruitment_api.root_resource_id
  path_part   = "search"
}

# API Gateway Method - POST /search
resource "aws_api_gateway_method" "search_post" {
  rest_api_id   = aws_api_gateway_rest_api.recruitment_api.id
  resource_id   = aws_api_gateway_resource.search.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration - Search Lambda
resource "aws_api_gateway_integration" "search_lambda" {
  rest_api_id = aws_api_gateway_rest_api.recruitment_api.id
  resource_id = aws_api_gateway_resource.search.id
  http_method = aws_api_gateway_method.search_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.search_handler.invoke_arn
}

# Lambda Permissions for API Gateway
resource "aws_lambda_permission" "api_gateway_upload" {
  statement_id  = "AllowAPIGatewayInvokeUpload"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upload_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.recruitment_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_search" {
  statement_id  = "AllowAPIGatewayInvokeSearch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.search_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.recruitment_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.upload_lambda,
    aws_api_gateway_integration.search_lambda
  ]

  rest_api_id = aws_api_gateway_rest_api.recruitment_api.id
  stage_name  = var.environment
}

# Outputs
output "api_endpoint" {
  value = aws_api_gateway_deployment.deployment.invoke_url
}

output "s3_bucket_name" {
  value = aws_s3_bucket.resume_bucket.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.candidates.name
}
