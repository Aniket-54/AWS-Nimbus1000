"""
Configuration file for AWS services integration
Centralized configuration for future AWS resource connections
"""
import os

# AWS Region Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# DynamoDB Configuration
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "Candidates")
DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", None)  # For local testing

# S3 Configuration
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "recruitment-resumes")
S3_RESUME_PREFIX = "resumes/"  # Folder structure in S3

# AWS Textract Configuration
TEXTRACT_ENABLED = os.environ.get("TEXTRACT_ENABLED", "false").lower() == "true"

# Amazon Bedrock Configuration
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v1")
BEDROCK_ENABLED = os.environ.get("BEDROCK_ENABLED", "false").lower() == "true"

# Cognito Configuration (for HR authentication)
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", "")

# Application Configuration
MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "10"))
SKILL_MATCH_WEIGHT = float(os.environ.get("SKILL_MATCH_WEIGHT", "0.6"))
SIMILARITY_WEIGHT = float(os.environ.get("SIMILARITY_WEIGHT", "0.4"))

# Local Development Configuration
LOCAL_DATA_PATH = os.environ.get("LOCAL_DATA_PATH", "data/resume_data.csv")
LOCAL_SKILLS_PATH = os.environ.get("LOCAL_SKILLS_PATH", "data/unique_skills.csv")
