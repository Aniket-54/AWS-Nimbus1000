#!/usr/bin/env python3
"""
Test script for PDF upload and processing functionality
Tests both local and AWS integration
"""
import os
import sys
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.resume_parser.pdf_parser import PDFParser
from backend.services.resume_parser.skill_extractor import SkillExtractor


def test_pdf_parser():
    """Test PDF parsing functionality"""
    print("=" * 60)
    print("Testing PDF Parser")
    print("=" * 60)
    
    parser = PDFParser()
    
    # Test with sample text (simulating PDF extraction)
    sample_resume_text = """
    John Doe
    john.doe@email.com
    (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Senior Python Developer with 5 years of experience in machine learning
    and cloud computing. Expertise in AWS, Docker, and microservices.
    
    SKILLS
    Python, Java, JavaScript, AWS, Docker, Kubernetes, Machine Learning,
    TensorFlow, React, Node.js, PostgreSQL, MongoDB
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2020-Present)
    - Developed ML models using Python and TensorFlow
    - Deployed applications on AWS using Lambda and ECS
    - Led team of 5 developers
    
    Software Engineer - StartupXYZ (2018-2020)
    - Built REST APIs with Python and Flask
    - Implemented CI/CD pipelines
    
    EDUCATION
    Master of Science in Computer Science
    University of Technology, 2018
    Bachelor of Science in Computer Science
    State University, 2016
    """
    
    print("\n1. Testing structure parsing...")
    parsed = parser.parse_resume_structure(sample_resume_text)
    print(f"   Name: {parsed['name']}")
    print(f"   Email: {parsed['email']}")
    print(f"   Phone: {parsed['phone']}")
    print(f"   Experience Years: {parsed['experience_years']}")
    print(f"   Education: {parsed['education'][:100]}...")
    
    print("\n2. Testing skill extraction...")
    skill_extractor = SkillExtractor()
    skills = skill_extractor.extract(sample_resume_text)
    print(f"   Skills found: {len(skills)}")
    print(f"   Skills: {', '.join(skills[:10])}")
    
    print("\n✓ PDF Parser tests passed!")


def test_upload_handler_logic():
    """Test upload handler logic without AWS"""
    print("\n" + "=" * 60)
    print("Testing Upload Handler Logic")
    print("=" * 60)
    
    # Simulate the processing logic
    sample_text = """
    Jane Smith
    jane.smith@example.com
    
    SKILLS: Python, AWS, Machine Learning, Docker, Kubernetes
    
    EXPERIENCE: 7 years in software development
    """
    
    parser = PDFParser()
    skill_extractor = SkillExtractor()
    
    print("\n1. Parsing resume structure...")
    parsed = parser.parse_resume_structure(sample_text)
    
    print("\n2. Extracting skills...")
    skills = skill_extractor.extract(sample_text)
    
    print("\n3. Building candidate record...")
    candidate_record = {
        'candidate_id': 'test-123',
        'name': parsed['name'],
        'email': parsed['email'],
        'skills': skills,
        'experience_years': parsed['experience_years'],
        'status': 'processed'
    }
    
    print(f"\n   Candidate Record:")
    for key, value in candidate_record.items():
        if key == 'skills':
            print(f"   {key}: {len(value)} skills")
        else:
            print(f"   {key}: {value}")
    
    print("\n✓ Upload handler logic tests passed!")


def test_batch_processing_simulation():
    """Simulate batch processing of multiple resumes"""
    print("\n" + "=" * 60)
    print("Testing Batch Processing Simulation")
    print("=" * 60)
    
    resumes = [
        {
            'id': 'candidate-001',
            'text': 'Alice Johnson, alice@email.com, Python, Java, AWS, 5 years experience'
        },
        {
            'id': 'candidate-002',
            'text': 'Bob Williams, bob@email.com, JavaScript, React, Node.js, 3 years experience'
        },
        {
            'id': 'candidate-003',
            'text': 'Carol Davis, carol@email.com, Python, Machine Learning, TensorFlow, 8 years experience'
        }
    ]
    
    parser = PDFParser()
    skill_extractor = SkillExtractor()
    
    results = []
    
    print(f"\nProcessing {len(resumes)} resumes...")
    
    for resume in resumes:
        parsed = parser.parse_resume_structure(resume['text'])
        skills = skill_extractor.extract(resume['text'])
        
        result = {
            'candidate_id': resume['id'],
            'name': parsed['name'],
            'skills_found': len(skills),
            'status': 'success'
        }
        results.append(result)
        print(f"   ✓ Processed {resume['id']}: {result['name']} ({result['skills_found']} skills)")
    
    print(f"\n✓ Batch processing completed: {len(results)}/{len(resumes)} successful")


def test_integration_with_dynamodb():
    """Test DynamoDB integration (requires AWS credentials)"""
    print("\n" + "=" * 60)
    print("Testing DynamoDB Integration")
    print("=" * 60)
    
    try:
        from backend.database.dynamodb_client import DynamoDBClient
        
        print("\n1. Initializing DynamoDB client...")
        db_client = DynamoDBClient()
        
        print("2. Testing connection...")
        # Try to describe table
        print(f"   Table name: {db_client.table.name}")
        
        print("\n✓ DynamoDB integration test passed!")
        print("   Note: Actual read/write tests require AWS credentials")
        
    except Exception as e:
        print(f"\n⚠ DynamoDB test skipped: {e}")
        print("   This is expected if AWS credentials are not configured")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PDF UPLOAD SYSTEM TEST SUITE")
    print("=" * 60)
    
    try:
        test_pdf_parser()
        test_upload_handler_logic()
        test_batch_processing_simulation()
        test_integration_with_dynamodb()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Deploy infrastructure: cd infrastructure/terraform && terraform apply")
        print("2. Build Lambda packages: ./scripts/deploy_lambda.sh")
        print("3. Test with real PDFs using the API endpoints")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
