# Backend Deployment - Quick Start Checklist

## 📋 Complete Checklist

### Phase 1: Prerequisites (15 minutes)

```powershell
# 1. Check Python
python --version  # Need 3.11+

# 2. Install Terraform
# Download from: https://www.terraform.io/downloads
# Extract to C:\terraform
# Add to PATH

# 3. Install AWS CLI
# Download from: https://aws.amazon.com/cli/
# Run installer

# 4. Configure AWS
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)

# 5. Test connection
aws sts get-caller-identity
```

### Phase 2: Install Dependencies (5 minutes)

```powershell
cd "C:\C DRIVE\Ashwath\college\AWS-Nimbus1000"

pip install -r backend/requirements.txt
python -m spacy download en_core_web_md
python backend/test_implementation.py
```

### Phase 3: Build Lambda Packages (10 minutes)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy_lambda.ps1

# Verify
dir lambda_packages
# Should see: upload_handler.zip, batch_processor.zip, search_handler.zip
```

### Phase 4: Configure Terraform (2 minutes)

```powershell
# Edit infrastructure/terraform/variables.tf
# Change S3 bucket name to something unique:
# "recruitment-resumes-YOUR-NAME-12345"
```

### Phase 5: Deploy to AWS (10 minutes)

```powershell
cd infrastructure/terraform

terraform init
terraform plan
terraform apply
# Type: yes

# Get API endpoint
terraform output api_endpoint
# Copy this URL!
```

### Phase 6: Connect Frontend (2 minutes)

```powershell
# Edit frontend/config.js
# Set:
#   enabled: true
#   baseUrl: 'YOUR-API-ENDPOINT'

# Test
start frontend/index.html
```

---

## 🎯 Total Time: ~45 minutes

---

## ✅ Success Indicators

After each phase, you should see:

**Phase 1:**
```
{
    "UserId": "...",
    "Account": "...",
    "Arn": "..."
}
```

**Phase 2:**
```
✓ ALL FILES VERIFIED!
```

**Phase 3:**
```
Lambda packages created successfully!
```

**Phase 5:**
```
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.

Outputs:
api_endpoint = "https://abc123.execute-api.us-east-1.amazonaws.com/dev"
```

**Phase 6:**
- Frontend opens
- Can upload PDFs
- Can search candidates

---

## 🚨 Common Issues

### "terraform not found"
```powershell
# Add to PATH manually:
$env:Path += ";C:\terraform"
# Or restart terminal after installation
```

### "Unable to locate credentials"
```powershell
aws configure
# Re-enter your credentials
```

### "BucketAlreadyExists"
```powershell
# Change bucket name in variables.tf to something unique
```

### Lambda package too large
```powershell
# Normal - packages are 50-100MB
# Terraform handles upload automatically
```

---

## 📞 Need Help?

Check detailed guide: `DEPLOY_STEP_BY_STEP.md`

---

## 🎉 You're Done!

Your recruitment assistant is now live on AWS!

Test it:
1. Open frontend/index.html
2. Upload a PDF resume
3. Enter: "Python developer with AWS"
4. Click "Analyse Candidates"
5. See results!
