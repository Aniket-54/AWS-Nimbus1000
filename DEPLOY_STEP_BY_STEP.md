# Backend Deployment - Complete Step-by-Step Guide

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] AWS Account created
- [ ] Python 3.11+ installed
- [ ] Terraform installed
- [ ] AWS CLI installed and configured
- [ ] Project dependencies installed

---

## Part 1: Install Prerequisites

### Step 1.1: Check What You Have

Open PowerShell and run:

```powershell
# Check Python
python --version
# Should show: Python 3.11.x or higher

# Check pip
pip --version

# Check Terraform
terraform --version
# If this fails, Terraform is not installed

# Check AWS CLI
aws --version
# If this fails, AWS CLI is not installed
```

### Step 1.2: Install Terraform

**Option A: Download Manually**

1. Go to: https://www.terraform.io/downloads
2. Click **Windows** → **AMD64**
3. Download the ZIP file
4. Extract `terraform.exe` to `C:\terraform\`
5. Add to PATH:
   ```powershell
   # Run PowerShell as Administrator
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\terraform", "Machine")
   ```
6. Close and reopen PowerShell
7. Test: `terraform --version`

**Option B: Use Installation Script**

```powershell
# Run PowerShell as Administrator
powershell -ExecutionPolicy Bypass -File install_terraform.ps1
# Close and reopen PowerShell
terraform --version
```

### Step 1.3: Install AWS CLI

1. Download from: https://aws.amazon.com/cli/
2. Run the installer (MSI file)
3. Follow installation wizard
4. Close and reopen PowerShell
5. Test: `aws --version`

---

## Part 2: Configure AWS Credentials

### Step 2.1: Get AWS Access Keys

1. Log in to AWS Console: https://console.aws.amazon.com
2. Click your name (top right) → **Security credentials**
3. Scroll to **Access keys**
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)**
6. Check the box and click **Next**
7. Click **Create access key**
8. **IMPORTANT:** Copy both:
   - Access key ID
   - Secret access key
   (You won't see the secret again!)

### Step 2.2: Configure AWS CLI

```powershell
aws configure
```

Enter when prompted:
```
AWS Access Key ID: [paste your access key]
AWS Secret Access Key: [paste your secret key]
Default region name: us-east-1
Default output format: json
```

### Step 2.3: Verify AWS Connection

```powershell
# Test AWS connection
aws sts get-caller-identity
```

You should see your AWS account info. If you get an error, your credentials are wrong.

---

## Part 3: Install Python Dependencies

### Step 3.1: Navigate to Project

```powershell
cd "C:\C DRIVE\Ashwath\college\AWS-Nimbus1000"
```

### Step 3.2: Install Requirements

```powershell
# Install Python packages
pip install -r backend/requirements.txt
```

This installs:
- pandas
- spacy
- boto3
- PyPDF2
- pdfplumber

### Step 3.3: Download spaCy Model

```powershell
python -m spacy download en_core_web_md
```

This downloads the NLP model (may take 2-3 minutes).

### Step 3.4: Verify Installation

```powershell
python backend/test_implementation.py
```

You should see: "✓ ALL FILES VERIFIED!"

---

## Part 4: Build Lambda Packages

### Step 4.1: Run Build Script

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy_lambda.ps1
```

This will:
- Create `lambda_packages/` folder
- Install dependencies for each Lambda
- Create 3 ZIP files:
  - `upload_handler.zip`
  - `batch_processor.zip`
  - `search_handler.zip`

**This takes 5-10 minutes** (installing dependencies).

### Step 4.2: Verify Packages Created

```powershell
dir lambda_packages
```

You should see 3 ZIP files.

---

## Part 5: Configure Terraform

### Step 5.1: Update S3 Bucket Name

S3 bucket names must be globally unique. Edit `infrastructure/terraform/variables.tf`:

```powershell
notepad infrastructure/terraform/variables.tf
```

Change this line:
```hcl
default     = "recruitment-resumes-bucket"
```

To something unique:
```hcl
default     = "recruitment-resumes-YOUR-NAME-12345"
```

Save and close.

### Step 5.2: Review Configuration

Check `infrastructure/terraform/variables.tf`:
- `aws_region` = "us-east-1" (or your preferred region)
- `project_name` = "recruitment-assistant"
- `environment` = "dev"
- `s3_bucket_name` = your unique name
- `dynamodb_table_name` = "Candidates"

---

## Part 6: Deploy with Terraform

### Step 6.1: Navigate to Terraform Directory

```powershell
cd infrastructure/terraform
```

### Step 6.2: Initialize Terraform

```powershell
terraform init
```

This downloads the AWS provider. You should see:
```
Terraform has been successfully initialized!
```

### Step 6.3: Plan Deployment

```powershell
terraform plan
```

This shows what will be created:
- S3 bucket
- DynamoDB table
- 3 Lambda functions
- API Gateway
- IAM roles
- CloudWatch logs

Review the output. You should see: "Plan: X to add, 0 to change, 0 to destroy"

### Step 6.4: Deploy Everything

```powershell
terraform apply
```

Type `yes` when prompted.

**This takes 5-10 minutes.**

You'll see resources being created:
```
aws_s3_bucket.resume_bucket: Creating...
aws_dynamodb_table.candidates: Creating...
aws_lambda_function.upload_handler: Creating...
...
Apply complete! Resources: X added, 0 changed, 0 destroyed.
```

### Step 6.5: Get API Endpoint

```powershell
terraform output api_endpoint
```

Copy this URL! You'll need it for the frontend.

Example: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev`

---

## Part 7: Verify Deployment

### Step 7.1: Check S3 Bucket

```powershell
aws s3 ls | findstr recruitment
```

You should see your bucket listed.

### Step 7.2: Check DynamoDB Table

```powershell
aws dynamodb describe-table --table-name Candidates
```

You should see table details.

### Step 7.3: Check Lambda Functions

```powershell
aws lambda list-functions | findstr recruitment
```

You should see 3 functions listed.

### Step 7.4: Check API Gateway

```powershell
aws apigateway get-rest-apis
```

You should see your API listed.

---

## Part 8: Test the API

### Step 8.1: Test Search Endpoint

```powershell
# Go back to project root
cd ../..

# Test search (replace YOUR-API-ENDPOINT)
curl -X POST "https://YOUR-API-ENDPOINT/dev/search" -H "Content-Type: application/json" -d "{\"query\":\"Python developer\"}"
```

You should get a JSON response with results.

### Step 8.2: View Lambda Logs

```powershell
aws logs tail /aws/lambda/recruitment-assistant-search-handler --follow
```

Press Ctrl+C to stop.

---

## Part 9: Migrate Data (Optional)

### Step 9.1: Set Environment Variables

```powershell
$env:AWS_REGION = "us-east-1"
$env:DYNAMODB_TABLE_NAME = "Candidates"
```

### Step 9.2: Run Migration

```powershell
python scripts/migrate_csv_to_dynamodb.py
```

This uploads your CSV data to DynamoDB.

---

## Part 10: Connect Frontend

### Step 10.1: Update Frontend Config

Edit `frontend/config.js`:

```powershell
notepad frontend/config.js
```

Change:
```javascript
AWS: {
  enabled: true,  // Change to true
  baseUrl: 'https://YOUR-API-ENDPOINT',  // Paste your API endpoint
  stage: 'dev'
}
```

Save and close.

### Step 10.2: Test Frontend

```powershell
start frontend/index.html
```

Or use a local server:
```powershell
cd frontend
python -m http.server 8000
# Open: http://localhost:8000
```

---

## Troubleshooting

### Error: "terraform not found"
- Terraform not installed or not in PATH
- Solution: Follow Step 1.2 again

### Error: "Unable to locate credentials"
- AWS CLI not configured
- Solution: Run `aws configure` (Step 2.2)

### Error: "BucketAlreadyExists"
- S3 bucket name not unique
- Solution: Change bucket name in variables.tf (Step 5.1)

### Error: Lambda package too large
- Dependencies too big
- Solution: Remove unnecessary files from lambda_packages

### Error: "Access Denied"
- AWS user doesn't have permissions
- Solution: Add AdministratorAccess policy to your IAM user

---

## Success Checklist

- [ ] Terraform initialized successfully
- [ ] All resources created (terraform apply)
- [ ] API endpoint obtained
- [ ] Search endpoint returns results
- [ ] Frontend config updated
- [ ] Frontend connects to API

---

## What Was Created

### AWS Resources:
1. **S3 Bucket** - Stores resume PDFs
2. **DynamoDB Table** - Stores candidate data
3. **Lambda Functions** (3):
   - upload-handler - Handles PDF uploads
   - batch-processor - Processes S3 uploads
   - search-handler - Searches candidates
4. **API Gateway** - REST API with /upload and /search
5. **IAM Roles** - Permissions for Lambda
6. **CloudWatch Logs** - Logging for debugging

### Costs:
- Free tier: Most services free for first year
- After free tier: ~$4-5/month for 1000 resumes

---

## Next Steps

1. ✅ Backend deployed
2. ✅ Frontend connected
3. ⏳ Test PDF uploads
4. ⏳ Add authentication (Cognito)
5. ⏳ Deploy frontend to S3
6. ⏳ Add custom domain

---

## Quick Reference Commands

```powershell
# Deploy
cd infrastructure/terraform
terraform init
terraform apply

# Get API endpoint
terraform output api_endpoint

# View logs
aws logs tail /aws/lambda/FUNCTION-NAME --follow

# Destroy everything
terraform destroy
```

---

Your backend is now deployed and ready to use!
