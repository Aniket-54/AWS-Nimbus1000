#!/bin/bash
# Lambda deployment script for recruitment assistant

set -e

echo "Starting Lambda deployment process..."

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAMBDA_PACKAGES_DIR="$PROJECT_ROOT/lambda_packages"
BACKEND_DIR="$PROJECT_ROOT/backend"
DATA_DIR="$PROJECT_ROOT/data"

# Create lambda packages directory
mkdir -p "$LAMBDA_PACKAGES_DIR"

# Function to create Lambda deployment package
create_lambda_package() {
    local function_name=$1
    local handler_file=$2
    local package_name="${function_name}.zip"
    
    echo "Creating package for $function_name..."
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    
    # Install dependencies
    pip install -r "$PROJECT_ROOT/backend/requirements.txt" -t "$temp_dir" --quiet
    
    # Copy backend code
    cp -r "$BACKEND_DIR" "$temp_dir/"
    
    # Copy data files (for local fallback)
    mkdir -p "$temp_dir/data"
    cp "$DATA_DIR"/*.csv "$temp_dir/data/" 2>/dev/null || true
    
    # Download spaCy model
    python -m spacy download en_core_web_md --target "$temp_dir" 2>/dev/null || echo "SpaCy model already exists"
    
    # Create zip package
    cd "$temp_dir"
    zip -r "$LAMBDA_PACKAGES_DIR/$package_name" . -q
    cd -
    
    # Cleanup
    rm -rf "$temp_dir"
    
    echo "Package created: $LAMBDA_PACKAGES_DIR/$package_name"
}

# Create packages for each Lambda function
echo "Building Lambda packages..."

create_lambda_package "upload_handler" "backend/api/upload_resume_lambda.py"
create_lambda_package "batch_processor" "backend/api/batch_upload_lambda.py"
create_lambda_package "search_handler" "backend/api/search_candidates_lambda.py"

echo ""
echo "Lambda packages created successfully!"
echo "Packages location: $LAMBDA_PACKAGES_DIR"
echo ""
echo "Next steps:"
echo "1. Deploy infrastructure: cd infrastructure/terraform && terraform apply"
echo "2. Or manually upload packages to AWS Lambda console"
echo "3. Configure environment variables in Lambda console"
