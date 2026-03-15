# Backend Deployment Guide

## Overview
This backend provides candidate screening and ranking services for the recruitment assistant. It's designed for AWS Lambda deployment with future integration to DynamoDB, S3, Textract, Bedrock, and Cognito.

## Local Development Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_md
```

### Running Locally
```python
from backend.api.search_candidates_lambda import service

# Test the service
query = "Python developer with machine learning experience"
results = service(query)
print(results)
```

## AWS Deployment

### 1. Lambda Function Setup

#### Create Lambda Function
- Runtime: Python 3.9+
- Handler: `backend.api.search_candidates_lambda.lambda_handler`
- Memory: 512 MB (adjust based on dataset size)
- Timeout: 30 seconds

#### Lambda Layer for Dependencies
```bash
# Create layer directory
mkdir python
pip install -r backend/requirements.txt -t python/
python -m spacy download en_core_web_md -d python/

# Create layer zip
zip -r lambda-layer.zip python/

# Upload to AWS Lambda Layers
aws lambda publish-layer-version \
    --layer-name recruitment-dependencies \
    --zip-file fileb://lambda-layer.zip \
    --compatible-runtimes python3.9
```

#### Environment Variables
```
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=Candidates
S3_BUCKET_NAME=recruitment-resumes
MAX_RESULTS=10
SKILL_MATCH_WEIGHT=0.6
SIMILARITY_WEIGHT=0.4
```

### 2. API Gateway Setup

#### Create REST API
- Method: POST
- Path: `/search-candidates`
- Integration: Lambda Function
- Request body format:
```json
{
  "query": "Python developer with AWS experience"
}
```

#### Enable CORS
```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
}
```

### 3. DynamoDB Setup

#### Create Table
```bash
aws dynamodb create-table \
    --table-name Candidates \
    --attribute-definitions \
        AttributeName=candidate_id,AttributeType=S \
        AttributeName=skill,AttributeType=S \
    --key-schema \
        AttributeName=candidate_id,KeyType=HASH \
    --global-secondary-indexes \
        IndexName=SkillIndex,KeySchema=[{AttributeName=skill,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    --billing-mode PAY_PER_REQUEST
```

#### Migrate CSV Data to DynamoDB
```python
from backend.database.dynamodb_client import DynamoDBClient
from backend.services.data_loader.dataset_loader import DatasetLoader
import uuid

# Load CSV data
loader = DatasetLoader()
candidates = loader.get_candidates()

# Add candidate_id to each record
for candidate in candidates:
    candidate['candidate_id'] = str(uuid.uuid4())

# Batch write to DynamoDB
db_client = DynamoDBClient()
db_client.batch_write_candidates(candidates)
```

### 4. S3 Setup

#### Create S3 Bucket
```bash
aws s3 mb s3://recruitment-resumes
aws s3api put-bucket-versioning \
    --bucket recruitment-resumes \
    --versioning-configuration Status=Enabled
```

#### Configure Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::recruitment-resumes/*"
    }
  ]
}
```

### 5. IAM Permissions

#### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/Candidates",
        "arn:aws:dynamodb:*:*:table/Candidates/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::recruitment-resumes/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "textract:DetectDocumentText",
        "textract:AnalyzeDocument"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### 6. Cognito Setup (Optional - for HR Authentication)

#### Create User Pool
```bash
aws cognito-idp create-user-pool \
    --pool-name recruitment-hr-users \
    --auto-verified-attributes email
```

#### Create App Client
```bash
aws cognito-idp create-user-pool-client \
    --user-pool-id <pool-id> \
    --client-name recruitment-app
```

## Testing

### Test Lambda Function
```bash
aws lambda invoke \
    --function-name search-candidates \
    --payload '{"query": "Python developer"}' \
    response.json
```

### Test API Gateway
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/search-candidates \
    -H "Content-Type: application/json" \
    -d '{"query": "Python developer with machine learning"}'
```

## Monitoring

### CloudWatch Logs
- Lambda execution logs: `/aws/lambda/search-candidates`
- Monitor for errors and performance metrics

### CloudWatch Metrics
- Lambda invocations
- Lambda duration
- Lambda errors
- DynamoDB read/write capacity

## Cost Optimization

1. Use DynamoDB on-demand billing for variable workload
2. Implement Lambda reserved concurrency for predictable traffic
3. Use S3 Intelligent-Tiering for resume storage
4. Enable CloudWatch Logs retention policy (7-30 days)

## Future Enhancements

1. Implement caching with ElastiCache/DynamoDB DAX
2. Add Amazon Bedrock for semantic search
3. Integrate AWS Textract for PDF resume parsing
4. Add SQS for asynchronous processing
5. Implement Step Functions for complex workflows
