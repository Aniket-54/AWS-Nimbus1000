ge: 'dev'             // API stage
  }
};
```

Your frontend is now ready to connect to the backend API!
 Styles
├── config.js               # API configuration (NEW)
├── app-integrated.js       # Integrated app (NEW)
├── app.js                  # Original app (CSV only)
└── react-app.tsx           # Placeholder
```

## Configuration Reference

```javascript
// config.js structure
const API_CONFIG = {
  LOCAL: {
    enabled: true,           // Use local/CSV mode
    baseUrl: 'http://localhost:5000'
  },
  AWS: {
    enabled: false,          // Use AWS API
    baseUrl: '',             // Your API Gateway URL
    stan config.js
```

## File Structure

```
frontend/
├── index.html              # Main app page (updated)
├── login.html              # Login page
├── styles.css              #loy frontend to S3 + CloudFront

## Deployment Options

### Option 1: Local Files
- Open `frontend/index.html` directly in browser
- Works for testing with CSV files

### Option 2: Local Server
```bash
cd frontend
python -m http.server 8000
# Open http://localhost:8000
```

### Option 3: S3 + CloudFront (Production)
```bash
# Upload frontend to S3
aws s3 sync frontend/ s3://your-frontend-bucket/ --exclude "*.md"

# Configure S3 for static website hosting
# Add CloudFront distribution
# Update API endpoint i0`

### API Not Found
- Verify API endpoint URL in config.js
- Check terraform output: `terraform output api_endpoint`
- Ensure Lambda functions are deployed

### Upload Fails
- Check file size (Lambda limit: 6MB for direct upload)
- For larger files, upload directly to S3
- Check CloudWatch logs for errors

## Next Steps

1. ✅ Frontend integrated with backend
2. ⏳ Deploy to AWS
3. ⏳ Update config.js with API endpoint
4. ⏳ Test PDF uploads
5. ⏳ Test candidate search
6. ⏳ Add authentication (Cognito)
7. ⏳ Dep1. Add CORS headers to Lambda responses
2. Or serve frontend from same domain as API
3. Or use a local server: `python -m http.server 800e": "John Doe",
      "skills": ["Python", "AWS"],
      "final_score": 0.85,
      "skill_match_score": 0.90,
      "similarity_score": 0.78
    }
  ]
}
```

## Testing

### Test with Local CSV
1. Keep `API_CONFIG.AWS.enabled = false`
2. Upload CSV file
3. Works offline with mock scores

### Test with AWS API
1. Deploy backend: `terraform apply`
2. Set `API_CONFIG.AWS.enabled = true`
3. Add API endpoint URL
4. Upload PDFs and search

## Troubleshooting

### CORS Errors
If you see CORS errors in browser console:

ch score

## API Endpoints Used

### POST /upload
Uploads a PDF resume

**Request:**
```json
{
  "file": "base64_encoded_pdf",
  "filename": "resume.pdf"
}
```

**Response:**
```json
{
  "message": "Resume processed successfully",
  "data": {
    "candidate_id": "uuid",
    "skills_found": 15
  }
}
```

### POST /search
Searches and ranks candidates

**Request:**
```json
{
  "query": "Python developer with AWS experience"
}
```

**Response:**
```json
{
  "results": [
    {
      "candidate_id": "123",
      "namResults
2. View full profile with AI reasoning
3. See skills, experience, and mat
```bash
# Keep AWS disabled in config.js
# Use the original app.js for CSV-only testing
```

## Usage

### Upload PDFs
1. Open `frontend/index.html` in browser
2. Drag & drop PDF files or click to browse
3. Enter job description
4. Click "Analyse Candidates"
5. PDFs are uploaded to S3 and processed

### Search Candidates
1. Enter job description in the prompt box
2. Click "Analyse Candidates"
3. Backend ranks all candidates
4. Results displayed with AI scores

### View Details
1. Click any candidate row in     baseUrl: 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com',  // Add your API endpoint
    stage: 'dev'
  }
};
```

Get your API endpoint by running:
```bash
cd infrastructure/terraform
terraform output api_endpoint
```

### Step 3: Test Locally (Optional)

For local testing without AWS:
API unavailable
✅ Real-time search and filtering

## Setup Instructions

### Step 1: Use the Integrated Version

The HTML is already updated to use the integrated version. The files are:
- `frontend/config.js` - Configuration
- `frontend/app-integrated.js` - Main app with API integration
- `frontend/index.html` - Updated to load both files

### Step 2: Configure API Endpoint

After deploying to AWS, update `frontend/config.js`:

```javascript
const API_CONFIG = {
  AWS: {
    enabled: true,  // Change to true
API calls)
    ↓
Backend API (Lambda/Local)
    ↓
DynamoDB / CSV
```

### Features

✅ Upload PDF resumes to S3 via API
✅ Search candidates using backend ranking algorithm
✅ Display AI scores and reasoning
✅ Fallback to local CSV if nd is now connected to the backend API! The system supports:
- PDF resume uploads via API
- Candidate search using backend ranking
- Fallback to local CSV processing
- Seamless switching between local and AWS deployment

## Files Created

1. **frontend/config.js** - API configuration
2. **frontend/app-integrated.js** - Integrated version with API calls
3. **FRONTEND_INTEGRATION.md** - This guide

## How It Works

### Architecture

```
Frontend (HTML/JS)
    ↓
config.js (API endpoints)
    ↓
app-integrated.js (# Frontend-Backend Integration Guide

## Overview

Your HireAI fronte