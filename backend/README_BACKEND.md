# Recruitment Assistant Backend

## Overview
This backend system provides intelligent candidate screening and ranking services for HR teams. It processes large volumes of job applications efficiently using skill matching and semantic similarity algorithms.

## Architecture

### Current Implementation (CSV-based)
```
┌─────────────────┐
│  Lambda Handler │ ← API Gateway
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Service │
    └────┬─────┘
         │
    ┌────▼──────────┬──────────────┬─────────────┐
    │               │              │             │
┌───▼────┐  ┌──────▼─────┐  ┌────▼─────┐  ┌───▼────┐
│Dataset │  │Query Parser│  │  Ranker  │  │Matcher │
│Loader  │  └────────────┘  └──────────┘  └────────┘
└────────┘
```

### Future AWS Architecture
```
┌──────────┐     ┌─────────────┐     ┌────────────┐
│ Cognito  │────▶│ API Gateway │────▶│   Lambda   │
└──────────┘     └─────────────┘     └─────┬──────┘
                                            │
                 ┌──────────────────────────┼──────────────┐
                 │                          │              │
            ┌────▼─────┐            ┌──────▼──────┐  ┌───▼────┐
            │ DynamoDB │            │     S3      │  │Bedrock │
            │(Metadata)│            │  (Resumes)  │  │  (NLP) │
            └──────────┘            └──────┬──────┘  └────────┘
                                           │
                                    ┌──────▼──────┐
                                    │  Textract   │
                                    │(PDF Parsing)│
                                    └─────────────┘
```

## Directory Structure

```
backend/
├── api/
│   ├── __init__.py
│   └── search_candidates_lambda.py    # Lambda handler for candidate search
├── database/
│   ├── __init__.py
│   ├── dynamodb_schema.txt            # DynamoDB table design
│   └── dynamodb_client.py             # DynamoDB operations wrapper
├── query_parser/
│   ├── __init__.py
│   └── query_parser.py                # Extract skills from job descriptions
├── services/
│   ├── __init__.py
│   ├── aws_integration.py             # S3, Textract, Bedrock clients
│   ├── auth_service.py                # Cognito authentication
│   ├── data_loader/
│   │   ├── __init__.py
│   │   └── dataset_loader.py          # Load candidate data
│   ├── job_matcher/
│   │   ├── __init__.py
│   │   ├── matcher.py                 # Skill matching algorithm
│   │   └── similarity_engine.py       # Semantic similarity (spaCy)
│   ├── ranking_engine/
│   │   ├── __init__.py
│   │   └── ranker.py                  # Candidate ranking logic
│   └── resume_parser/
│       ├── __init__.py
│       ├── resume_loader.py           # Resume data operations
│       └── skill_extractor.py         # Extract skills from text
├── __init__.py
├── config.py                          # Configuration and environment variables
├── requirements.txt                   # Python dependencies
├── test_local.py                      # Local testing script
├── DEPLOYMENT.md                      # AWS deployment guide
└── README_BACKEND.md                  # This file
```

## Core Components

### 1. API Layer (`api/`)
- **search_candidates_lambda.py**: AWS Lambda handler that processes candidate search requests
  - Accepts job description queries
  - Returns top 10 ranked candidates
  - Integrates with API Gateway

### 2. Query Parser (`query_parser/`)
- **query_parser.py**: Extracts skills and keywords from job descriptions
  - Uses regex for keyword extraction
  - Future: Amazon Bedrock integration for advanced NLP

### 3. Data Loader (`services/data_loader/`)
- **dataset_loader.py**: Loads candidate data from CSV
  - Current: Reads from local CSV file
  - Future: Queries DynamoDB with pagination

### 4. Job Matcher (`services/job_matcher/`)
- **matcher.py**: Calculates exact skill match percentage
  - Handles list and string skill formats
  - Case-insensitive matching
- **similarity_engine.py**: Computes semantic similarity using spaCy
  - Uses word embeddings for context understanding
  - Future: Amazon Bedrock embeddings

### 5. Ranking Engine (`services/ranking_engine/`)
- **ranker.py**: Ranks candidates using weighted scoring
  - 60% skill match + 40% semantic similarity (configurable)
  - Returns sorted list with scores

### 6. Resume Parser (`services/resume_parser/`)
- **resume_loader.py**: Loads and retrieves resume data
  - Future: S3 integration for PDF storage
- **skill_extractor.py**: Extracts skills from resume text
  - Uses predefined skill dictionary
  - Future: AWS Textract for PDF parsing

### 7. AWS Integration (`services/`)
- **aws_integration.py**: Wrapper classes for AWS services
  - S3Client: Resume storage and retrieval
  - TextractClient: PDF text extraction
  - BedrockClient: Advanced NLP and embeddings
- **auth_service.py**: Cognito authentication
  - User authentication and token verification
  - HR user management

### 8. Database (`database/`)
- **dynamodb_schema.txt**: DynamoDB table design
  - Candidate table with GSI for skill queries
- **dynamodb_client.py**: DynamoDB operations
  - CRUD operations for candidates
  - Batch write support

## Key Features

### Current Features
✓ Skill-based candidate matching  
✓ Semantic similarity scoring  
✓ Weighted ranking algorithm  
✓ Query parsing and keyword extraction  
✓ CSV data loading  
✓ Lambda-ready API handler  

### Future AWS Integrations
⏳ DynamoDB for scalable candidate storage  
⏳ S3 for resume PDF storage  
⏳ AWS Textract for PDF text extraction  
⏳ Amazon Bedrock for advanced NLP  
⏳ Cognito for HR user authentication  
⏳ CloudWatch for monitoring and logging  

## Configuration

All configuration is centralized in `config.py`:

```python
# AWS Services
AWS_REGION = "us-east-1"
DYNAMODB_TABLE_NAME = "Candidates"
S3_BUCKET_NAME = "recruitment-resumes"

# Ranking Weights
SKILL_MATCH_WEIGHT = 0.6
SIMILARITY_WEIGHT = 0.4

# Results
MAX_RESULTS = 10
```

## Installation

### Local Development
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md

# Run tests
python backend/test_local.py
```

### AWS Deployment
See `DEPLOYMENT.md` for complete AWS setup instructions.

## Usage

### Local Testing
```python
from backend.api.search_candidates_lambda import service

# Search for candidates
query = "Python developer with AWS and machine learning experience"
results = service(query)

# Display top candidates
for i, candidate in enumerate(results, 1):
    print(f"{i}. Score: {candidate['score']:.2f}")
    print(f"   Skills: {candidate['skills']}")
```

### Lambda Invocation
```json
{
  "body": "{\"query\": \"Python developer with AWS experience\"}"
}
```

### API Gateway Request
```bash
curl -X POST https://api.example.com/search-candidates \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer with machine learning"}'
```

## Algorithm Details

### Skill Matching
- Extracts skills from candidate resume (stored as list or comma-separated string)
- Compares with required skills from job description
- Score = (Matched Skills) / (Required Skills)

### Semantic Similarity
- Uses spaCy word embeddings (en_core_web_md model)
- Computes cosine similarity between job requirements and candidate responsibilities
- Captures contextual meaning beyond exact keyword matches

### Final Ranking
- Final Score = (0.6 × Skill Match) + (0.4 × Semantic Similarity)
- Candidates sorted by final score in descending order
- Top 10 candidates returned

## Error Handling

All components include comprehensive error handling:
- File not found errors for missing datasets
- Empty query validation
- Graceful fallbacks (e.g., word overlap if spaCy unavailable)
- AWS service error handling with ClientError exceptions

## Testing

Run the test suite:
```bash
python backend/test_local.py
```

Tests cover:
- Query parsing
- Dataset loading
- Skill matching
- Semantic similarity
- Ranking algorithm
- Lambda handler

## Performance Considerations

### Current (CSV-based)
- Loads entire dataset into memory
- Suitable for datasets up to 10,000 candidates
- O(n) time complexity for ranking

### Future (DynamoDB)
- Pagination for large datasets
- GSI for skill-based queries
- DynamoDB DAX for caching
- Parallel processing with Lambda concurrency

## Security

### Current
- Input validation for queries
- Error message sanitization

### Future AWS Security
- Cognito for authentication
- IAM roles with least privilege
- API Gateway throttling
- VPC for Lambda (if needed)
- S3 bucket encryption
- DynamoDB encryption at rest

## Monitoring

### Future CloudWatch Integration
- Lambda execution metrics
- DynamoDB read/write capacity
- API Gateway request counts
- Custom metrics for ranking quality
- Log aggregation and analysis

## Contributing

When adding new features:
1. Add comprehensive docstrings
2. Include error handling
3. Update tests in `test_local.py`
4. Document AWS integration points
5. Update this README

## License

Internal use only - Recruitment Assistant Project
