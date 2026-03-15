# System Architecture - PDF Resume Upload & Processing

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  (Frontend - React App / API Client / AWS Console)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (REST)                         │
│  Endpoints: /upload (POST), /search (POST)                      │
│  Features: HTTPS, Throttling, API Keys, CORS                    │
└────────┬────────────────────────────────────────┬───────────────┘
         │                                        │
         │ /upload                                │ /search
         ▼                                        ▼
┌─────────────────────┐                 ┌─────────────────────┐
│  UPLOAD LAMBDA      │                 │  SEARCH LAMBDA      │
│  - Validate PDF     │                 │  - Parse query      │
│  - Upload to S3     │                 │  - Load candidates  │
│  - Extract text     │                 │  - Rank & score     │
│  - Parse structure  │                 │  - Return top 10    │
│  - Extract skills   │                 └──────────┬──────────┘
│  - Store in DB      │                            │
└─────────┬───────────┘                            │
          │                                        │
          ▼                                        ▼
┌─────────────────────┐                 ┌─────────────────────┐
│    S3 BUCKET        │                 │     DYNAMODB        │
│  - Resume PDFs      │◄────────────────│  - Candidate data   │
│  - Versioning       │                 │  - Skills index     │
│  - Encryption       │                 │  - Email index      │
│  - Event triggers   │                 │  - Timestamp index  │
└─────────┬───────────┘                 └─────────────────────┘
          │                                        ▲
          │ S3 Event                               │
          │ (ObjectCreated)                        │
          ▼                                        │
┌─────────────────────┐                           │
│  BATCH LAMBDA       │                           │
│  - Triggered by S3  │                           │
│  - Process PDFs     │                           │
│  - Parallel workers │───────────────────────────┘
│  - Error handling   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   AWS TEXTRACT      │
│  - PDF extraction   │
│  - OCR support      │
│  - Multi-page       │
└─────────────────────┘
```

## Data Flow - Single PDF Upload

```
1. User uploads PDF
   │
   ▼
2. API Gateway receives request
   │
   ▼
3. Upload Lambda validates PDF
   │
   ▼
4. PDF uploaded to S3
   │
   ├─► 5a. Textract extracts text (if enabled)
   │   OR
   └─► 5b. Local parser extracts text
   │
   ▼
6. Extract skills from text
   │
   ▼
7. Parse structure (name, email, phone, etc.)
   │
   ▼
8. Store candidate record in DynamoDB
   │
   ▼
9. Return success response to user
```

## Data Flow - Batch Upload

```
1. User uploads multiple PDFs to S3
   │
   ▼
2. S3 triggers Lambda for each PDF
   │
   ▼
3. Batch Lambda processes in parallel
   │
   ├─► Worker 1: Process PDF 1
   ├─► Worker 2: Process PDF 2
   ├─► Worker 3: Process PDF 3
   ├─► Worker 4: Process PDF 4
   └─► Worker 5: Process PDF 5
   │
   ▼
4. Each worker:
   - Extracts text
   - Extracts skills
   - Parses structure
   - Stores in DynamoDB
   │
   ▼
5. All results aggregated
   │
   ▼
6. Summary logged to CloudWatch
```

## Data Flow - Candidate Search

```
1. User submits job description
   │
   ▼
2. API Gateway receives search request
   │
   ▼
3. Search Lambda parses query
   │
   ▼
4. Extract required skills from query
   │
   ▼
5. Load candidates from DynamoDB
   │
   ▼
6. For each candidate:
   ├─► Calculate skill match score
   └─► Calculate semantic similarity
   │
   ▼
7. Combine scores (weighted)
   │
   ▼
8. Sort by final score
   │
   ▼
9. Return top 10 candidates
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  Query Parser    │      │  Dataset Loader  │           │
│  │  - Extract skills│      │  - Load from CSV │           │
│  │  - Regex parsing │      │  - Load from DB  │           │
│  └──────────────────┘      └──────────────────┘           │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  PDF Parser      │      │  Skill Extractor │           │
│  │  - pdfplumber    │      │  - Match skills  │           │
│  │  - PyPDF2        │      │  - Known skills  │           │
│  │  - Textract      │      │  - Dictionary    │           │
│  └──────────────────┘      └──────────────────┘           │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  Job Matcher     │      │  Similarity Eng. │           │
│  │  - Skill match   │      │  - spaCy NLP     │           │
│  │  - Score calc    │      │  - Semantic sim. │           │
│  └──────────────────┘      └──────────────────┘           │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  Ranking Engine  │      │  Batch Processor │           │
│  │  - Combine scores│      │  - Parallel exec │           │
│  │  - Sort results  │      │  - Error handling│           │
│  └──────────────────┘      └──────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## AWS Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS ACCOUNT                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  COMPUTE                                           │   │
│  │  - Lambda: upload-handler (512MB, 5min)           │   │
│  │  - Lambda: batch-processor (1024MB, 15min)        │   │
│  │  - Lambda: search-handler (512MB, 1min)           │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  STORAGE                                           │   │
│  │  - S3: recruitment-resumes-bucket                  │   │
│  │    • Versioning enabled                            │   │
│  │    • Encryption: AES256                            │   │
│  │    • Lifecycle: Archive after 90 days              │   │
│  │  - DynamoDB: Candidates table                      │   │
│  │    • Partition key: candidate_id                   │   │
│  │    • GSI: EmailIndex, TimestampIndex               │   │
│  │    • Billing: On-demand                            │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  API & NETWORKING                                  │   │
│  │  - API Gateway: recruitment-api                    │   │
│  │    • Stage: dev, prod                              │   │
│  │    • Binary media types: application/pdf           │   │
│  │    • CORS enabled                                  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  AI/ML SERVICES                                    │   │
│  │  - Textract: PDF text extraction                   │   │
│  │  - Bedrock: Advanced NLP (optional)                │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  SECURITY & MONITORING                             │   │
│  │  - IAM: Lambda execution role                      │   │
│  │  - CloudWatch: Logs & metrics                      │   │
│  │  - Cognito: User authentication (planned)          │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### DynamoDB Table: Candidates

```
Primary Key: candidate_id (String)

Attributes:
├── candidate_id (String) - UUID
├── filename (String) - Original PDF filename
├── s3_key (String) - S3 object key
├── resume_text (String) - Extracted text
├── skills (List) - Array of skill strings
├── name (String) - Candidate name
├── email (String) - Email address
├── phone (String) - Phone number
├── experience_years (Number) - Years of experience
├── education (String) - Education details
├── upload_timestamp (String) - ISO timestamp
└── status (String) - processed/failed/pending

Global Secondary Indexes:
├── EmailIndex
│   └── Partition key: email
└── TimestampIndex
    └── Partition key: upload_timestamp
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Network Security                                 │
│  ├── HTTPS only (TLS 1.2+)                                 │
│  ├── API Gateway throttling                                │
│  └── VPC for Lambda (optional)                             │
│                                                             │
│  Layer 2: Authentication & Authorization                   │
│  ├── Cognito user pools (planned)                          │
│  ├── API Gateway API keys                                  │
│  └── IAM roles with least privilege                        │
│                                                             │
│  Layer 3: Data Security                                    │
│  ├── S3 encryption at rest (AES256)                        │
│  ├── DynamoDB encryption at rest                           │
│  ├── Encryption in transit (HTTPS)                         │
│  └── S3 bucket policies                                    │
│                                                             │
│  Layer 4: Application Security                             │
│  ├── Input validation (PDF only)                           │
│  ├── File size limits                                      │
│  ├── Malware scanning (planned)                            │
│  └── Rate limiting                                         │
│                                                             │
│  Layer 5: Monitoring & Auditing                            │
│  ├── CloudWatch logs                                       │
│  ├── CloudTrail audit logs                                 │
│  ├── CloudWatch alarms                                     │
│  └── Error tracking                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Local Development                                      │
│     ├── Write code                                         │
│     ├── Run tests locally                                  │
│     └── Verify functionality                               │
│                                                             │
│  2. Build Lambda Packages                                  │
│     ├── Install dependencies                               │
│     ├── Copy backend code                                  │
│     ├── Download spaCy model                               │
│     └── Create ZIP packages                                │
│                                                             │
│  3. Infrastructure as Code                                 │
│     ├── Terraform init                                     │
│     ├── Terraform plan                                     │
│     └── Terraform apply                                    │
│                                                             │
│  4. Deploy Lambda Functions                                │
│     ├── Upload ZIP to Lambda                               │
│     ├── Configure environment variables                    │
│     └── Set up triggers                                    │
│                                                             │
│  5. Data Migration                                         │
│     ├── Export CSV data                                    │
│     ├── Transform records                                  │
│     └── Batch write to DynamoDB                            │
│                                                             │
│  6. Testing & Validation                                   │
│     ├── Test upload endpoint                               │
│     ├── Test search endpoint                               │
│     ├── Test batch processing                              │
│     └── Monitor CloudWatch logs                            │
│                                                             │
│  7. Production Deployment                                  │
│     ├── Enable authentication                              │
│     ├── Configure monitoring                               │
│     ├── Set up alarms                                      │
│     └── Deploy frontend                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Scaling Strategy

```
Current Capacity:
├── Lambda: 1000 concurrent executions
├── S3: Unlimited storage
├── DynamoDB: On-demand (auto-scaling)
└── API Gateway: 10,000 requests/second

For 10,000+ resumes/day:
├── Add SQS queue between S3 and Lambda
├── Implement Lambda reserved concurrency
├── Use DynamoDB provisioned capacity
├── Add ElastiCache for search results
├── Use CloudFront for API caching
└── Consider ECS/Fargate for heavy processing
```

## Cost Breakdown

```
Monthly Cost (1000 resumes):

S3 Storage (100GB)
├── Storage: $2.30
└── Requests: $0.01

DynamoDB
├── Writes: $0.01
└── Reads: $0.01

Lambda
├── Invocations: $0.20
└── Duration: $0.10

Textract
└── Pages: $1.50

API Gateway
└── Requests: $0.01

Total: ~$4-5/month
```

---

This architecture is designed for:
- **Scalability**: Handle 10,000+ resumes/day
- **Reliability**: 99.9% uptime with AWS services
- **Security**: Multiple layers of protection
- **Cost-efficiency**: Pay only for what you use
- **Maintainability**: Infrastructure as code
