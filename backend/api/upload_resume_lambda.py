"""
AWS Lambda handler for resume PDF upload and processing
Handles: File upload, S3 storage, Textract extraction, DynamoDB storage
"""
import json
import base64
import uuid
from datetime import datetime
from backend.services.aws_integration import S3Client, TextractClient
from backend.database.dynamodb_client import DynamoDBClient
from backend.services.resume_parser.pdf_parser import PDFParser
from backend.services.resume_parser.skill_extractor import SkillExtractor
from backend.config import S3_BUCKET_NAME, TEXTRACT_ENABLED


def process_resume(file_content, filename, candidate_id=None):
    """
    Core service logic for resume processing
    Args:
        file_content: Binary PDF content
        filename: Original filename
        candidate_id: Optional candidate ID (generated if not provided)
    Returns:
        Dictionary with processing results
    """
    if candidate_id is None:
        candidate_id = str(uuid.uuid4())
    
    # Initialize clients
    s3_client = S3Client()
    pdf_parser = PDFParser()
    skill_extractor = SkillExtractor()
    db_client = DynamoDBClient()
    
    # Step 1: Upload PDF to S3
    s3_key = s3_client.upload_resume_content(file_content, candidate_id)
    if not s3_key:
        raise Exception("Failed to upload resume to S3")
    
    # Step 2: Extract text from PDF
    if TEXTRACT_ENABLED:
        # Use AWS Textract for better accuracy
        textract_client = TextractClient()
        resume_text = textract_client.extract_text_from_s3(S3_BUCKET_NAME, s3_key)
    else:
        # Fallback to local PDF parsing
        resume_text = pdf_parser.extract_text_from_bytes(file_content)
    
    if not resume_text:
        raise Exception("Failed to extract text from PDF")
    
    # Step 3: Extract skills from resume text
    skills = skill_extractor.extract(resume_text)
    
    # Step 4: Parse additional information (name, email, experience, etc.)
    parsed_data = pdf_parser.parse_resume_structure(resume_text)
    
    # Step 5: Store in DynamoDB
    candidate_record = {
        'candidate_id': candidate_id,
        'filename': filename,
        's3_key': s3_key,
        'resume_text': resume_text,
        'skills': skills,
        'name': parsed_data.get('name', 'Unknown'),
        'email': parsed_data.get('email', ''),
        'phone': parsed_data.get('phone', ''),
        'experience_years': parsed_data.get('experience_years', 0),
        'education': parsed_data.get('education', ''),
        'upload_timestamp': datetime.utcnow().isoformat(),
        'status': 'processed'
    }
    
    success = db_client.put_candidate(candidate_record)
    if not success:
        raise Exception("Failed to store candidate in database")
    
    return {
        'candidate_id': candidate_id,
        's3_key': s3_key,
        'skills_found': len(skills),
        'status': 'success'
    }


def lambda_handler(event, context):
    """
    AWS Lambda entry point for resume upload
    Supports:
    - Single file upload via base64 encoded body
    - Multipart form data (API Gateway)
    Args:
        event: API Gateway event with file data
        context: Lambda context object
    Returns:
        API Gateway response with processing results
    """
    try:
        # Extract file content from event
        if event.get('isBase64Encoded'):
            # Base64 encoded file upload
            file_content = base64.b64decode(event['body'])
            filename = event.get('headers', {}).get('x-filename', 'resume.pdf')
        elif 'body' in event:
            # JSON body with base64 file
            body = json.loads(event['body'])
            file_content = base64.b64decode(body['file'])
            filename = body.get('filename', 'resume.pdf')
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No file content provided"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        # Validate file type
        if not filename.lower().endswith('.pdf'):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Only PDF files are supported"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        # Process the resume
        result = process_resume(file_content, filename)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Resume processed successfully",
                "data": result
            }),
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
