# Windows Deployment Guide

## Step-by-Step Instructions for Windows

### Prerequisites Check

Before starting, verify you have:

```powershell
# Check Python
python --version
# Should show Python 3.11 or higher

# Check pip
pip --version

# Check if AWS CLI is installed (optional for now)
aws --version

# Check if Terraform is installed
terraform --version
```

If any are missing, install them first.

## Step 1: Install Python Dependencies

```powershell
# Navigate to project root
cd "C:\C DRIVE\Ashwath\college\AWS-Nimbus1000"

# Install dependencies
pip install -r backend/requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md
```

## Step 2: Build Lambda Packages

You have two options:

### Option A: Using PowerShell Script (Recommended for Windows)

```powershell
# Run the PowerShell script
powershell -ExecutionPolicy Bypass -File scripts/deploy_lambda.ps1
```

### Option B: Manual Build (if script fails)

```powershell
# Create packages directory
New-Item -ItemType Directory -Force -Path lambda_packages

# Create temporary directory
$temp = "$env:TEMP\lambda_build"
New-Item -ItemType Directory -Force -Path $temp

# Install dependencies
pip install -r backend/requirements.txt -t $temp

# Copy backend code
Copy-Item -Path backend -Destination $temp -Recurse

# Copy data files
New-Item -ItemType Directory -Force -Path "$temp\data"
Copy-Item -Path "data\*.csv" -Destination "$temp\data"

# Create ZIP (for upload_handler)
Compress-Archive -Path "$temp\*" -DestinationPath "lambda_packages\upload_handler.zip" -Force

# Repeat for other functions...
```

## Step 3: Deploy Infrastructure with Terraform

### Install Terraform (if not installed)

```powershell
# Using Chocolatey
choco install terraform

# Or download from: https://www.terraform.io/downloads
```

### Deploy

```powershell
# Navigate to terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Apply the configuration
terraform apply
# Type 'yes' when prompted
```

## Step 4: Configure AWS Credentials

If you haven't configured AWS CLI:

```powershell
# Install AWS CLI
# Download from: https://aws.amazon.com/cli/

# Configure credentials
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

## Step 5: Migrate Data to DynamoDB (Optional)

```powershell
# Set environment variables
$env:AWS_REGION = "us-east-1"
$env:DYNAMODB_TABLE_NAME = "Candidates"

# Run migration
python scripts/migrate_csv_to_dynamodb.py
```

## Troubleshooting

### Issue: "pip install" fails

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Try again
pip install -r backend/requirements.txt
```

### Issue: "Compress-Archive" is slow or fails

```powershell
# Install 7-Zip
choco install 7zip

# Use 7-Zip instead
7z a -tzip lambda_packages\upload_handler.zip $temp\*
```

### Issue: "terraform not found"

```powershell
# Add Terraform to PATH or use full path
# Download from: https://www.terraform.io/downloads
# Extract to C:\terraform
# Add C:\terraform to PATH
```

### Issue: Permission denied on scripts

```powershell
# Run PowerShell as Administrator
# Or change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Quick Commands Reference

```powershell
# Full deployment in one go
pip install -r backend/requirements.txt
python -m spacy download en_core_web_md
powershell -ExecutionPolicy Bypass -File scripts/deploy_lambda.ps1
cd infrastructure/terraform
terraform init
terraform apply

# Test after deployment
python backend/test_pdf_upload.py
```

## Alternative: Deploy Without Terraform

If Terraform is causing issues, you can deploy manually:

1. **Create S3 Bucket** in AWS Console
2. **Create DynamoDB Table** in AWS Console
3. **Upload Lambda packages** manually
4. **Create API Gateway** manually
5. **Configure triggers** manually

See `backend/DEPLOYMENT_PDF.md` for detailed manual steps.
