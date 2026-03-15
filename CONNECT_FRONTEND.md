# Connect Frontend to Backend - Quick Guide

## What Was Done

✅ Created `frontend/config.js` - API configuration
✅ Created `frontend/app-integrated.js` - API-connected version
✅ Updated `frontend/index.html` - Now loads integrated version

## How to Use

### Step 1: Deploy Backend (if not done)

```powershell
# Build Lambda packages
powershell -ExecutionPolicy Bypass -File scripts/deploy_lambda.ps1

# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform apply

# Get API endpoint
terraform output api_endpoint
```

### Step 2: Configure Frontend

Edit `frontend/config.js`:

```javascript
const API_CONFIG = {
  AWS: {
    enabled: true,  // Change to true
    baseUrl: 'YOUR-API-ENDPOINT-HERE',  // Paste from terraform output
    stage: 'dev'
  }
};
```

### Step 3: Open Frontend

```powershell
# Option 1: Open directly
start frontend/index.html

# Option 2: Use local server
cd frontend
python -m http.server 8000
# Then open: http://localhost:8000
```

## Features

- Upload PDF resumes → Stored in S3
- Search candidates → Ranked by backend AI
- View results → With AI scores
- Fallback to CSV if API unavailable

## Test It

1. Open `frontend/index.html`
2. Upload a PDF resume
3. Enter: "Python developer with AWS"
4. Click "Analyse Candidates"
5. See ranked results!

## Troubleshooting

**API not working?**
- Check `config.js` has correct URL
- Verify backend is deployed
- Check browser console for errors

**CORS errors?**
- Use local server: `python -m http.server 8000`
- Or add CORS headers to Lambda

Your frontend and backend are now connected!
