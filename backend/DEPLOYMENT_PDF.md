# PDF Resume Upload Deployment Guide

## Overview
This guide covers deploying the PDF resume upload and processing system to AWS.

## Architecture

```
User Upload → API Gateway → Lambda (Upload Handler) → S3 → Lambda (Batch Processor) → DynamoDB
                                                              ↓
                                                         Textract (PDF parsing)
```

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured (`aws configure`)
3. Terraform installed (v1.0+)
4. Python 3.11+
5. Required Python packages: `pip install -r backend/requirements.txt`

## Deployment Steps

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md
```

### 2. Build Lambda Packages

```bash
# Make deployment script executable
chmod +x scripts/deploy_lambda.sh

# Build Lambda packages
./scripts/deploy_lambda.sh
```

This creates three Lambda deployment packages:
- `upload_handler.zip` - Handles single PDF uploads via API
- `batch_processor.zip` - Processes PDFs uploaded to S3
- `search_handler.zip` - Searches candidates in DynamoDB

### 3. Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan

# Deploy infrastructure
terraform apply
```

This creates:
- S3 bucket for resume storage
- DynamoDB table for candidate data
- 3 Lambda functions
- API Gateway with /upload and /search endpoints
- IAM roles and permissions
- S3 event triggers

### 4. Migrate Existing CSV Data (Optional)

```bash
# Set environment variables
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=Candidates

# Run migration script
python scripts/migrate_csv_to_dynamodb.py --csv data/resume_data.csv
```

### 5. Enable AWS Services

#### Enable Textract
```bash
# Textract is enabled by default in most regions
# Verify access:
aws textract detect-document-text --help
```

#### Enable Bedrock (Optional - for advanced NLP)
```bash
# Request access to Bedrock models in AWS Console
# Navigate to: Amazon Bedrock → Model access → Request access
```

### 6. Test the Deployment

#### Test Upload Endpoint
```bash
# Get API endpoint from Terraform output
API_ENDPOINT=$(terraform output -raw api_endpoint)

# Upload a test PDF
curl -X POST "$API_ENDPOINT/upload" \
  -H "Content-Type: application/json" \
  -H "x-filename: test_resume.pdf" \
  --data-binary "@test_resume.pdf" \
  | jq
```

#### Test Search Endpoint
```bash
curl -X POST "$API_ENDPOINT/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer with AWS experience"}' \
  | jq
```

#### Test S3 Batch Processing
```bash
# Upload directly to S3 (triggers batch processor)
aws s3 cp test_resume.pdf s3://recruitment-resumes-bucket/resumes/test-candidate-123.pdf

# Check CloudWatch logs
aws logs tail /aws/lambda/recruitment-assistant-batch-processor --follow
```

## Configuration

### Environment Variables

Set these in Lambda console or Terraform:

```bash
# Required
AWS_REGION=us-east-1
S3_BUCKET_NAME=recruitment-resumes-bucket
DYNAMODB_TABLE_NAME=Candidates

# Optional
TEXTRACT_ENABLED=true
BEDROCK_ENABLED=false
MAX_RESULTS=10
SKILL_MATCH_WEIGHT=0.6
SIMILARITY_WEIGHT=0.4
```

### Lambda Function Settings

Recommended configurations:

**Upload Handler:**
- Memory: 512 MB
- Timeout: 300 seconds (5 minutes)
- Runtime: Python 3.11

**Batch Processor:**
- Memory: 1024 MB
- Timeout: 900 seconds (15 minutes)
- Runtime: Python 3.11

**Search Handler:**
- Memory: 512 MB
- Timeout: 60 seconds
- Runtime: Python 3.11

## Usage

### Single PDF Upload via API

```python
import requests
import base64

# Read PDF file
with open('resume.pdf', 'rb') as f:
    pdf_content = f.read()

# Upload to API
response = requests.post(
    'https://your-api-endpoint.amazonaws.com/dev/upload',
    json={
        'file': base64.b64encode(pdf_content).decode('utf-8'),
        'filename': 'resume.pdf'
    }
)

print(response.json())
# Output: {'message': 'Resume processed successfully', 'data': {...}}
```

### Batch Upload to S3

```bash
# Upload multiple PDFs
for file in resumes/*.pdf; do
    filename=$(basename "$file" .pdf)
    aws s3 cp "$file" "s3://recruitment-resumes-bucket/resumes/${filename}.pdf"
done

# Lambda automatically processes each upload
```

### Search Candidates

```python
import requests

response = requests.post(
    'https://your-api-endpoint.amazonaws.com/dev/search',
    json={'query': 'Python developer with machine learning experience'}
)

candidates = response.json()['results']
for candidate in candidates:
    print(f"{candidate['name']}: {candidate['final_score']}")
```

## Monitoring

### CloudWatch Logs

```bash
# Upload handler logs
aws logs tail /aws/lambda/recruitment-assistant-upload-handler --follow

# Batch processor logs
aws logs tail /aws/lambda/recruitment-assistant-batch-processor --follow

# Search handler logs
aws logs tail /aws/lambda/recruitment-assistant-search-handler --follow
```

### CloudWatch Metrics

Monitor these metrics:
- Lambda invocations
- Lambda errors
- Lambda duration
- S3 object count
- DynamoDB read/write capacity

### Cost Estimation

Approximate costs for 1000 resumes/month:

- S3 Storage: $0.023/GB (~$2.30 for 100GB)
- DynamoDB: $1.25/million writes (~$0.01)
- Lambda: $0.20/million requests (~$0.20)
- Textract: $1.50/1000 pages (~$1.50)
- API Gateway: $3.50/million requests (~$0.01)

**Total: ~$4-5/month for 1000 resumes**

## Troubleshooting

### PDF Extraction Fails

1. Check CloudWatch logs for errors
2. Verify PDF is not encrypted or password-protected
3. Try enabling Textract: `TEXTRACT_ENABLED=true`
4. Check Lambda timeout settings

### DynamoDB Write Errors

1. Verify IAM permissions
2. Check DynamoDB table exists
3. Verify table name in environment variables
4. Check for throttling in CloudWatch metrics

### S3 Upload Fails

1. Verify bucket exists and is accessible
2. Check IAM permissions for S3
3. Verify bucket name in configuration
4. Check CORS settings if uploading from browser

### Lambda Timeout

1. Increase timeout in Lambda settings
2. Increase memory allocation
3. Optimize PDF processing (use Textract instead of local parsing)
4. Process large batches asynchronously

## Security Best Practices

1. **Enable S3 encryption** - Already configured in Terraform
2. **Use VPC for Lambda** - Add VPC configuration if needed
3. **Enable API Gateway authentication** - Add Cognito or API keys
4. **Rotate IAM credentials** - Use AWS Secrets Manager
5. **Enable CloudTrail** - Audit all API calls
6. **Scan PDFs for malware** - Add antivirus scanning layer
7. **Implement rate limiting** - Use API Gateway throttling

## Scaling Considerations

### For 10,000+ resumes/month:

1. **Use SQS queue** between S3 and Lambda for better control
2. **Enable DynamoDB auto-scaling** or use on-demand billing
3. **Use Lambda reserved concurrency** to control costs
4. **Implement caching** with ElastiCache for frequent searches
5. **Use Step Functions** for complex workflows
6. **Consider ECS/Fargate** for very large batch processing

## Cleanup

To remove all resources:

```bash
cd infrastructure/terraform
terraform destroy
```

This removes:
- All Lambda functions
- API Gateway
- DynamoDB table (data will be lost!)
- S3 bucket (must be empty first)
- IAM roles and policies

## Next Steps

1. Add Cognito authentication for HR users
2. Implement frontend UI for uploads
3. Add email notifications for processing completion
4. Integrate Amazon Bedrock for better skill matching
5. Add resume anonymization (remove names, gender)
6. Implement advanced search filters
7. Add analytics dashboard
