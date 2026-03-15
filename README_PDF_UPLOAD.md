# PDF Resume Upload System

## Overview

This system now supports uploading and processing large volumes of PDF resumes. The architecture is designed to handle thousands of resumes efficiently using AWS services.

## Key Features

✅ **PDF Parsing** - Extracts text from PDF resumes using pdfplumber and PyPDF2
✅ **AWS Textract Integration** - Optional cloud-based PDF extraction for better accuracy
✅ **Batch Processing** - Process multiple resumes in parallel
✅ **S3 Storage** - Secure storage for all resume PDFs
✅ **DynamoDB Database** - Scalable storage for candidate data
✅ **Automatic Skill Extraction** - Identifies skills from resume text
✅ **Structured Data Parsing** - Extracts name, email, phone, experience, education
✅ **API Endpoints** - RESTful API for uploads and searches
✅ **Event-Driven Processing** - S3 triggers Lambda for automatic processing

## Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ Upload PDF
       ▼
┌─────────────────┐
│  API Gateway    │
│   /upload       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Upload Lambda   │─────▶│  S3 Bucket   │
└─────────────────┘      └──────┬───────┘
                                │ Event Trigger
                                ▼
                         ┌──────────────┐
                         │Batch Lambda  │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌──────────────┐        ┌─────────────┐
            │  Textract    │        │  DynamoDB   │
            │(PDF Extract) │        │ (Candidates)│
            └──────────────┘        └─────────────┘
```

## New Files Added

### Core Processing
- `backend/services/resume_parser/pdf_parser.py` - PDF text extraction and parsing
- `backend/api/upload_resume_lambda.py` - Single PDF upload handler
- `backend/api/batch_upload_lambda.py` - S3-triggered batch processor
- `backend/services/batch_processor.py` - Parallel batch processing service

### Infrastructure
- `infrastructure/terraform/main.tf` - Complete AWS infrastructure as code
- `infrastructure/terraform/variables.tf` - Terraform configuration variables

### Deployment & Testing
- `scripts/deploy_lambda.sh` - Lambda package builder
- `scripts/migrate_csv_to_dynamodb.py` - CSV to DynamoDB migration
- `backend/test_pdf_upload.py` - Test suite for PDF processing
- `backend/DEPLOYMENT_PDF.md` - Detailed deployment guide

### Updated Files
- `backend/requirements.txt` - Added PyPDF2 and pdfplumber
- `backend/services/data_loader/dataset_loader.py` - Now supports DynamoDB
- `backend/services/aws_integration.py` - Added upload_resume_content method

## Quick Start

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
python -m spacy download en_core_web_md
```

### 2. Test Locally

```bash
# Run test suite
python backend/test_pdf_upload.py
```

### 3. Deploy to AWS

```bash
# Build Lambda packages
chmod +x scripts/deploy_lambda.sh
./scripts/deploy_lambda.sh

# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform apply
```

### 4. Migrate Existing Data

```bash
# Set environment variables
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=Candidates

# Run migration
python scripts/migrate_csv_to_dynamodb.py
```

## Usage Examples

### Upload Single PDF via API

```python
import requests
import base64

# Read PDF
with open('resume.pdf', 'rb') as f:
    pdf_content = base64.b64encode(f.read()).decode('utf-8')

# Upload
response = requests.post(
    'https://your-api.amazonaws.com/dev/upload',
    json={'file': pdf_content, 'filename': 'resume.pdf'}
)

print(response.json())
```

### Batch Upload to S3

```bash
# Upload multiple PDFs (auto-processed by Lambda)
aws s3 sync ./resumes/ s3://recruitment-resumes-bucket/resumes/
```

### Search Candidates

```python
import requests

response = requests.post(
    'https://your-api.amazonaws.com/dev/search',
    json={'query': 'Python developer with AWS experience'}
)

for candidate in response.json()['results']:
    print(f"{candidate['name']}: {candidate['final_score']}")
```

## Configuration

### Environment Variables

```bash
# Required
AWS_REGION=us-east-1
S3_BUCKET_NAME=recruitment-resumes-bucket
DYNAMODB_TABLE_NAME=Candidates

# Optional
TEXTRACT_ENABLED=true          # Use AWS Textract for PDF parsing
BEDROCK_ENABLED=false          # Use Bedrock for advanced NLP
USE_DYNAMODB=true              # Use DynamoDB instead of CSV
MAX_RESULTS=10                 # Number of search results
SKILL_MATCH_WEIGHT=0.6         # Weight for skill matching
SIMILARITY_WEIGHT=0.4          # Weight for semantic similarity
```

## API Endpoints

### POST /upload
Upload a single PDF resume

**Request:**
```json
{
  "file": "base64_encoded_pdf_content",
  "filename": "resume.pdf"
}
```

**Response:**
```json
{
  "message": "Resume processed successfully",
  "data": {
    "candidate_id": "uuid",
    "s3_key": "resumes/uuid.pdf",
    "skills_found": 15,
    "status": "success"
  }
}
```

### POST /search
Search for candidates

**Request:**
```json
{
  "query": "Python developer with machine learning experience"
}
```

**Response:**
```json
{
  "results": [
    {
      "candidate_id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "skills": ["Python", "Machine Learning", "AWS"],
      "final_score": 0.85,
      "skill_match_score": 0.90,
      "similarity_score": 0.78
    }
  ]
}
```

## Performance

### Capacity
- **Single PDF**: ~2-5 seconds processing time
- **Batch (100 PDFs)**: ~30-60 seconds with parallel processing
- **Storage**: Unlimited (S3 + DynamoDB)
- **Concurrent uploads**: 1000+ (Lambda auto-scaling)

### Cost Estimates (1000 resumes/month)
- S3 Storage: ~$2.30
- DynamoDB: ~$0.01
- Lambda: ~$0.20
- Textract: ~$1.50
- API Gateway: ~$0.01
- **Total: ~$4-5/month**

## Monitoring

### CloudWatch Logs
```bash
# View upload logs
aws logs tail /aws/lambda/recruitment-assistant-upload-handler --follow

# View batch processing logs
aws logs tail /aws/lambda/recruitment-assistant-batch-processor --follow
```

### Metrics to Monitor
- Lambda invocations and errors
- Lambda duration and memory usage
- S3 object count
- DynamoDB read/write capacity
- API Gateway request count

## Troubleshooting

### PDF Extraction Fails
1. Enable Textract: `TEXTRACT_ENABLED=true`
2. Check PDF is not encrypted
3. Increase Lambda timeout
4. Check CloudWatch logs

### DynamoDB Errors
1. Verify table exists
2. Check IAM permissions
3. Verify environment variables
4. Check for throttling

### Lambda Timeout
1. Increase timeout (max 15 minutes)
2. Increase memory allocation
3. Use Textract instead of local parsing
4. Process in smaller batches

## Security

✅ S3 encryption enabled
✅ DynamoDB encryption at rest
✅ IAM least-privilege permissions
✅ API Gateway HTTPS only
✅ CloudWatch logging enabled

**Recommended additions:**
- Add Cognito authentication
- Enable API Gateway API keys
- Implement rate limiting
- Add malware scanning
- Use VPC for Lambda

## Next Steps

1. ✅ PDF parsing implemented
2. ✅ Batch processing implemented
3. ✅ AWS infrastructure defined
4. ✅ Deployment scripts created
5. ⏳ Add Cognito authentication
6. ⏳ Build frontend UI
7. ⏳ Implement resume anonymization
8. ⏳ Add Bedrock integration
9. ⏳ Create analytics dashboard

## Support

For detailed deployment instructions, see `backend/DEPLOYMENT_PDF.md`

For testing, run: `python backend/test_pdf_upload.py`

For issues, check CloudWatch logs and verify AWS credentials.
