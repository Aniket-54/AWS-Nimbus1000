# Deployment Checklist - PDF Resume Upload System

## Pre-Deployment

### Local Environment Setup
- [ ] Python 3.11+ installed
- [ ] pip package manager installed
- [ ] Git installed and configured
- [ ] Code editor/IDE installed (VS Code, PyCharm, etc.)

### AWS Prerequisites
- [ ] AWS account created
- [ ] AWS CLI installed
- [ ] AWS credentials configured (`aws configure`)
- [ ] Appropriate IAM permissions (Lambda, S3, DynamoDB, API Gateway, Textract)
- [ ] Terraform installed (v1.0+)

### Dependencies Installation
- [ ] Run: `pip install -r backend/requirements.txt`
- [ ] Run: `python -m spacy download en_core_web_md`
- [ ] Verify: `python backend/test_implementation.py`

## Local Testing

### Unit Tests
- [ ] Run: `python backend/test_pdf_upload.py`
- [ ] Run: `python backend/test_local.py`
- [ ] All tests pass without errors

### Manual Testing
- [ ] Test PDF parsing with sample PDF
- [ ] Test skill extraction
- [ ] Test search functionality with CSV data
- [ ] Verify query parser works correctly

## Build & Package

### Lambda Packages
- [ ] Make script executable: `chmod +x scripts/deploy_lambda.sh`
- [ ] Run: `./scripts/deploy_lambda.sh`
- [ ] Verify packages created in `lambda_packages/`:
  - [ ] upload_handler.zip
  - [ ] batch_processor.zip
  - [ ] search_handler.zip

### Configuration Review
- [ ] Review `infrastructure/terraform/variables.tf`
- [ ] Update S3 bucket name (must be globally unique)
- [ ] Update DynamoDB table name if needed
- [ ] Set AWS region
- [ ] Set environment (dev/staging/prod)

## Infrastructure Deployment

### Terraform Initialization
- [ ] Navigate to: `cd infrastructure/terraform`
- [ ] Run: `terraform init`
- [ ] Verify providers downloaded successfully

### Terraform Planning
- [ ] Run: `terraform plan`
- [ ] Review resources to be created:
  - [ ] S3 bucket
  - [ ] DynamoDB table
  - [ ] 3 Lambda functions
  - [ ] API Gateway
  - [ ] IAM roles and policies
  - [ ] CloudWatch log groups
- [ ] Verify no errors in plan

### Terraform Apply
- [ ] Run: `terraform apply`
- [ ] Type `yes` to confirm
- [ ] Wait for deployment to complete (5-10 minutes)
- [ ] Note the API endpoint from output

### Verify Resources Created
- [ ] Check S3 bucket exists: `aws s3 ls | grep recruitment`
- [ ] Check DynamoDB table: `aws dynamodb describe-table --table-name Candidates`
- [ ] Check Lambda functions: `aws lambda list-functions | grep recruitment`
- [ ] Check API Gateway: `aws apigateway get-rest-apis`

## Data Migration (Optional)

### CSV to DynamoDB
- [ ] Set environment variables:
  ```bash
  export AWS_REGION=us-east-1
  export DYNAMODB_TABLE_NAME=Candidates
  ```
- [ ] Run: `python scripts/migrate_csv_to_dynamodb.py`
- [ ] Verify data migrated: `aws dynamodb scan --table-name Candidates --limit 5`

## Testing Deployed System

### API Endpoint Testing

#### Test Upload Endpoint
- [ ] Get API endpoint: `terraform output api_endpoint`
- [ ] Create test request:
  ```bash
  curl -X POST "https://YOUR-API-ENDPOINT/dev/upload" \
    -H "Content-Type: application/json" \
    -d '{"file": "BASE64_PDF", "filename": "test.pdf"}'
  ```
- [ ] Verify response: `{"message": "Resume processed successfully"}`
- [ ] Check S3: `aws s3 ls s3://recruitment-resumes-bucket/resumes/`
- [ ] Check DynamoDB: `aws dynamodb scan --table-name Candidates --limit 1`

#### Test Search Endpoint
- [ ] Create search request:
  ```bash
  curl -X POST "https://YOUR-API-ENDPOINT/dev/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "Python developer with AWS experience"}'
  ```
- [ ] Verify response contains candidate results
- [ ] Verify scores are calculated correctly

#### Test Batch Processing
- [ ] Upload PDF to S3:
  ```bash
  aws s3 cp test_resume.pdf s3://recruitment-resumes-bucket/resumes/test-123.pdf
  ```
- [ ] Wait 10-30 seconds for processing
- [ ] Check CloudWatch logs:
  ```bash
  aws logs tail /aws/lambda/recruitment-assistant-batch-processor --follow
  ```
- [ ] Verify candidate added to DynamoDB

## Monitoring Setup

### CloudWatch Logs
- [ ] Verify log groups created:
  - [ ] `/aws/lambda/recruitment-assistant-upload-handler`
  - [ ] `/aws/lambda/recruitment-assistant-batch-processor`
  - [ ] `/aws/lambda/recruitment-assistant-search-handler`
- [ ] Test log streaming: `aws logs tail LOG-GROUP-NAME --follow`

### CloudWatch Alarms (Recommended)
- [ ] Create alarm for Lambda errors
- [ ] Create alarm for Lambda duration
- [ ] Create alarm for DynamoDB throttling
- [ ] Create alarm for API Gateway 5xx errors

### Cost Monitoring
- [ ] Enable AWS Cost Explorer
- [ ] Set up billing alerts
- [ ] Review estimated monthly costs

## Security Hardening

### S3 Security
- [ ] Verify bucket encryption enabled
- [ ] Verify bucket versioning enabled
- [ ] Review bucket policies
- [ ] Enable access logging (optional)

### DynamoDB Security
- [ ] Verify encryption at rest enabled
- [ ] Review IAM policies
- [ ] Enable point-in-time recovery (optional)

### Lambda Security
- [ ] Review IAM execution role permissions
- [ ] Verify environment variables are set correctly
- [ ] Consider VPC configuration (optional)

### API Gateway Security
- [ ] Enable API keys (recommended)
- [ ] Configure throttling limits
- [ ] Enable CORS if needed
- [ ] Consider adding Cognito authentication

## Performance Optimization

### Lambda Configuration
- [ ] Review memory allocation (512MB for upload, 1024MB for batch)
- [ ] Review timeout settings (5min for upload, 15min for batch)
- [ ] Enable Lambda insights (optional)

### DynamoDB Configuration
- [ ] Verify on-demand billing mode
- [ ] Review GSI configuration
- [ ] Consider provisioned capacity for predictable workloads

### API Gateway Configuration
- [ ] Enable caching (optional)
- [ ] Configure throttling limits
- [ ] Review stage settings

## Documentation

### Update Documentation
- [ ] Update README.md with API endpoint
- [ ] Document any custom configurations
- [ ] Add team-specific deployment notes
- [ ] Update architecture diagrams if modified

### Create Runbooks
- [ ] Document common issues and solutions
- [ ] Create incident response procedures
- [ ] Document rollback procedures
- [ ] Create maintenance procedures

## Post-Deployment

### Validation
- [ ] Upload 5-10 test resumes
- [ ] Perform 10-20 test searches
- [ ] Verify all results are accurate
- [ ] Check CloudWatch metrics

### Performance Testing
- [ ] Test with large PDF (10+ pages)
- [ ] Test batch upload (10+ PDFs)
- [ ] Measure response times
- [ ] Verify parallel processing works

### User Acceptance Testing
- [ ] Share API endpoint with team
- [ ] Collect feedback on functionality
- [ ] Test with real-world resumes
- [ ] Verify search results quality

## Production Readiness

### Before Going Live
- [ ] Enable authentication (Cognito)
- [ ] Configure production domain
- [ ] Set up SSL certificate
- [ ] Enable WAF (Web Application Firewall)
- [ ] Configure backup strategy
- [ ] Set up disaster recovery plan

### Launch Checklist
- [ ] Notify stakeholders
- [ ] Update DNS records (if applicable)
- [ ] Monitor for first 24 hours
- [ ] Be ready for quick rollback
- [ ] Document any issues

## Maintenance

### Regular Tasks
- [ ] Review CloudWatch logs weekly
- [ ] Check cost reports monthly
- [ ] Update dependencies quarterly
- [ ] Review security settings quarterly
- [ ] Test backup/restore procedures

### Monitoring
- [ ] Set up daily health checks
- [ ] Monitor error rates
- [ ] Track API usage
- [ ] Review performance metrics

## Rollback Plan

### If Issues Occur
- [ ] Document the issue
- [ ] Check CloudWatch logs
- [ ] Verify AWS service status
- [ ] If needed, run: `terraform destroy`
- [ ] Restore from backup if data loss occurred

## Success Criteria

### System is Ready When:
- [ ] All tests pass
- [ ] API endpoints respond correctly
- [ ] PDFs are processed successfully
- [ ] Search returns accurate results
- [ ] Monitoring is in place
- [ ] Documentation is complete
- [ ] Team is trained
- [ ] Backup strategy is tested

## Next Steps After Deployment

### Phase 2 Features
- [ ] Add Cognito authentication
- [ ] Build frontend UI (React)
- [ ] Implement resume anonymization
- [ ] Add Bedrock integration
- [ ] Create analytics dashboard
- [ ] Add email notifications
- [ ] Implement advanced search filters

### Continuous Improvement
- [ ] Collect user feedback
- [ ] Monitor performance metrics
- [ ] Optimize costs
- [ ] Improve search accuracy
- [ ] Add new features based on needs

---

## Quick Reference Commands

```bash
# Build Lambda packages
./scripts/deploy_lambda.sh

# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Migrate data
python scripts/migrate_csv_to_dynamodb.py

# Test upload
curl -X POST "https://API-ENDPOINT/dev/upload" -d @test.json

# Test search
curl -X POST "https://API-ENDPOINT/dev/search" -d '{"query":"Python"}'

# View logs
aws logs tail /aws/lambda/FUNCTION-NAME --follow

# Destroy infrastructure
terraform destroy
```

---

**Deployment Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

**Deployed By:** _______________

**Deployment Date:** _______________

**API Endpoint:** _______________

**Notes:** _______________
