"""
AWS Lambda handler for batch resume processing
Triggered by S3 events when multiple PDFs are uploaded
"""
import json
from backend.services.aws_integration import S3Client, TextractClient
from backend.database.dynamodb_client import DynamoDBClient
from backend.services.resume_parser.pdf_parser import PDFParser
from backend.services.resume_parser.skill_extractor import SkillExtractor
from backend.config import TEXTRACT_ENABLED


def process_s3_resume(bucket, key):
    """
    Process a resume that was uploaded to S3
    Args:
        bucket: S3 bucket name
        key: S3 object key
    Returns:
        Processing result dictionary
    """
    # Extract candidate_id from S3 key (format: resumes/{candidate_id}.pdf)
    candidate_id = key.split('/')[-1].replace('.pdf', '')
    
    # Initialize clients
    s3_client = S3Client()
    pdf_parser = PDFParser()
    skill_extractor = SkillExtractor()
    db_client = DynamoDBClient()
    
    # Step 1: Extract text from PDF
    if TEXTRACT_ENABLED:
        textract_client = TextractClient()
        resume_text = textract_client.extract_text_from_s3(bucket, key)
    else:
        # Download and parse locally
        local_path = f"/tmp/{candidate_id}.pdf"
        s3_client.download_resume(key, local_path)
        resume_text = pdf_parser.extract_text_from_file(local_path)
    
    if not resume_text:
        return {'candidate_id': candidate_id, 'status': 'failed', 'error': 'Text extraction failed'}
    
    # Step 2: Extract skills
    skills = skill_extractor.extract(resume_text)
    
    # Step 3: Parse structure
    parsed_data = pdf_parser.parse_resume_structure(resume_text)
    
    # Step 4: Store in DynamoDB
    candidate_record = {
        'candidate_id': candidate_id,
        's3_key': key,
        'resume_text': resume_text,
        'skills': skills,
        'name': parsed_data.get('name', 'Unknown'),
        'email': parsed_data.get('email', ''),
        'phone': parsed_data.get('phone', ''),
        'experience_years': parsed_data.get('experience_years', 0),
        'education': parsed_data.get('education', ''),
        'status': 'processed'
    }
    
    db_client.put_candidate(candidate_record)
    
    return {'candidate_id': candidate_id, 'status': 'success', 'skills_found': len(skills)}


def lambda_handler(event, context):
    """
    S3 event-triggered Lambda handler
    Processes resumes uploaded directly to S3
    Args:
        event: S3 event notification
        context: Lambda context
    Returns:
        Processing summary
    """
    results = []
    
    try:
        # Process each S3 record in the event
        for record in event.get('Records', []):
            if record['eventName'].startswith('ObjectCreated'):
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                
                # Only process PDF files in the resumes folder
                if key.startswith('resumes/') and key.endswith('.pdf'):
                    result = process_s3_resume(bucket, key)
                    results.append(result)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Processed {len(results)} resumes",
                "results": results
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
