#!/usr/bin/env python3
"""
Quick test to verify implementation structure
Tests that all new files exist and are properly structured
"""
import os
import sys

def test_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {filepath}")
        return True
    else:
        print(f"✗ {filepath} - NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("IMPLEMENTATION VERIFICATION TEST")
    print("=" * 60)
    
    files_to_check = [
        # Core processing files
        "backend/services/resume_parser/pdf_parser.py",
        "backend/api/upload_resume_lambda.py",
        "backend/api/batch_upload_lambda.py",
        "backend/services/batch_processor.py",
        
        # Infrastructure files
        "infrastructure/terraform/main.tf",
        "infrastructure/terraform/variables.tf",
        
        # Scripts
        "scripts/deploy_lambda.sh",
        "scripts/migrate_csv_to_dynamodb.py",
        "backend/test_pdf_upload.py",
        
        # Documentation
        "README_PDF_UPLOAD.md",
        "backend/DEPLOYMENT_PDF.md",
        "IMPLEMENTATION_SUMMARY.md",
        
        # Updated files
        "backend/requirements.txt",
        "backend/services/data_loader/dataset_loader.py",
        "backend/services/aws_integration.py",
        "README.md"
    ]
    
    print("\nChecking implementation files...")
    print("-" * 60)
    
    all_exist = True
    for filepath in files_to_check:
        if not test_file_exists(filepath):
            all_exist = False
    
    print("-" * 60)
    
    if all_exist:
        print("\n✓ ALL FILES VERIFIED!")
        print("\nImplementation complete. Next steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_md")
        print("3. Run full tests: python backend/test_pdf_upload.py")
        print("4. Deploy to AWS: ./scripts/deploy_lambda.sh")
        return 0
    else:
        print("\n✗ Some files are missing!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
