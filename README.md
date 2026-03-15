# AWS-Nimbus1000 - Recruitment Assistant

## Overview
A recruitment assistant that helps HR teams screen large volumes of job applications efficiently. Upload PDF resumes, search by job description, and get the top 10 best-matching candidates ranked by skills and experience.

**Dataset:** https://www.kaggle.com/datasets/saugataroyarghya/resume-dataset

## ✅ What's New - PDF Upload System

The system now supports uploading and processing large volumes of PDF resumes:

- **PDF Parsing** - Extracts text from PDF resumes (pdfplumber + PyPDF2)
- **AWS Textract Integration** - Cloud-based PDF extraction for better accuracy
- **Batch Processing** - Process hundreds of resumes in parallel
- **S3 Storage** - Secure storage for all resume PDFs
- **DynamoDB Database** - Scalable storage replacing CSV
- **Automatic Skill Extraction** - Identifies skills from resume text
- **RESTful API** - Upload and search endpoints via API Gateway
- **Event-Driven** - S3 triggers Lambda for automatic processing

## Quick Start

### Local Testing
```bash
# Install dependencies
pip install -r backend/requirements.txt
python -m spacy download en_core_web_md

# Run tests
python backend/test_pdf_upload.py
python backend/test_local.py
```

### Deploy to AWS
```bash
# Build Lambda packages
chmod +x scripts/deploy_lambda.sh
./scripts/deploy_lambda.sh

# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform apply

# Migrate existing CSV data
python scripts/migrate_csv_to_dynamodb.py
```

## Architecture

```
User → API Gateway → Lambda → S3 → Lambda (Batch) → DynamoDB
                                      ↓
                                  Textract
```

## API Endpoints

**POST /upload** - Upload PDF resume
```bash
curl -X POST "https://api-endpoint/upload" \
  -H "Content-Type: application/json" \
  --data '{"file": "base64_pdf", "filename": "resume.pdf"}'
```

**POST /search** - Search candidates
```bash
curl -X POST "https://api-endpoint/search" \
  -H "Content-Type: application/json" \
  --data '{"query": "Python developer with AWS experience"}'
```

## Documentation

- **[README_PDF_UPLOAD.md](README_PDF_UPLOAD.md)** - PDF upload system overview
- **[backend/DEPLOYMENT_PDF.md](backend/DEPLOYMENT_PDF.md)** - Detailed deployment guide
- **[PROJECT_OVERVIEW.txt](PROJECT_OVERVIEW.txt)** - Complete project documentation
- **[backend/README_BACKEND.md](backend/README_BACKEND.md)** - Backend architecture

## AWS Services

- **Lambda** - Serverless compute for processing
- **API Gateway** - RESTful API endpoints
- **S3** - Resume PDF storage
- **DynamoDB** - Candidate database
- **Textract** - PDF text extraction
- **Bedrock** - Advanced NLP (optional)
- **Cognito** - Authentication (planned)

## Features

✅ PDF resume upload and parsing
✅ Batch processing of multiple resumes
✅ Skill extraction from resume text
✅ Semantic similarity matching
✅ Ranked candidate search
✅ RESTful API
✅ AWS infrastructure as code
✅ Local and cloud deployment

⏳ Frontend UI
⏳ Resume anonymization
⏳ Bedrock integration
⏳ Cognito authentication

## Cost Estimate

For 1000 resumes/month: ~$4-5/month
- S3: $2.30
- DynamoDB: $0.01
- Lambda: $0.20
- Textract: $1.50
- API Gateway: $0.01

## Testing

```bash
# Test PDF processing
python backend/test_pdf_upload.py

# Test search functionality
python backend/test_local.py
```

## Support

For issues or questions, check:
- CloudWatch logs for Lambda errors
- Terraform output for API endpoints
- Test scripts for validation
     
