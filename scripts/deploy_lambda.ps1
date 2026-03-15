# PowerShell script for Lambda deployment on Windows
# Lambda deployment script for recruitment assistant

Write-Host "Starting Lambda deployment process..." -ForegroundColor Green

# Configuration
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$LAMBDA_PACKAGES_DIR = Join-Path $PROJECT_ROOT "lambda_packages"
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$DATA_DIR = Join-Path $PROJECT_ROOT "data"

# Create lambda packages directory
New-Item -ItemType Directory -Force -Path $LAMBDA_PACKAGES_DIR | Out-Null

# Function to create Lambda deployment package
function Create-LambdaPackage {
    param(
        [string]$FunctionName,
        [string]$HandlerFile
    )
    
    $PackageName = "$FunctionName.zip"
    Write-Host "Creating package for $FunctionName..." -ForegroundColor Cyan
    
    # Create temporary directory
    $TempDir = Join-Path $env:TEMP "lambda_$FunctionName"
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    
    try {
        # Install dependencies
        Write-Host "  Installing dependencies..." -ForegroundColor Gray
        pip install -r "$PROJECT_ROOT\backend\requirements.txt" -t "$TempDir" --quiet
        
        # Copy backend code
        Write-Host "  Copying backend code..." -ForegroundColor Gray
        Copy-Item -Path $BACKEND_DIR -Destination $TempDir -Recurse -Force
        
        # Copy data files (for local fallback)
        $TempDataDir = Join-Path $TempDir "data"
        New-Item -ItemType Directory -Force -Path $TempDataDir | Out-Null
        if (Test-Path $DATA_DIR) {
            Copy-Item -Path "$DATA_DIR\*.csv" -Destination $TempDataDir -ErrorAction SilentlyContinue
        }
        
        # Download spaCy model
        Write-Host "  Downloading spaCy model..." -ForegroundColor Gray
        python -m spacy download en_core_web_md 2>$null
        
        # Create zip package
        Write-Host "  Creating ZIP package..." -ForegroundColor Gray
        $ZipPath = Join-Path $LAMBDA_PACKAGES_DIR $PackageName
        if (Test-Path $ZipPath) {
            Remove-Item $ZipPath -Force
        }
        
        # Use PowerShell's Compress-Archive
        Compress-Archive -Path "$TempDir\*" -DestinationPath $ZipPath -Force
        
        Write-Host "  Package created: $ZipPath" -ForegroundColor Green
    }
    finally {
        # Cleanup
        if (Test-Path $TempDir) {
            Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# Create packages for each Lambda function
Write-Host "`nBuilding Lambda packages...`n" -ForegroundColor Yellow

Create-LambdaPackage -FunctionName "upload_handler" -HandlerFile "backend/api/upload_resume_lambda.py"
Create-LambdaPackage -FunctionName "batch_processor" -HandlerFile "backend/api/batch_upload_lambda.py"
Create-LambdaPackage -FunctionName "search_handler" -HandlerFile "backend/api/search_candidates_lambda.py"

Write-Host "`nLambda packages created successfully!" -ForegroundColor Green
Write-Host "Packages location: $LAMBDA_PACKAGES_DIR" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Deploy infrastructure: cd infrastructure\terraform; terraform apply"
Write-Host "2. Or manually upload packages to AWS Lambda console"
Write-Host "3. Configure environment variables in Lambda console"
