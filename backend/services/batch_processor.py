"""
Batch processing service for handling multiple resume uploads
Supports SQS queue processing and parallel execution
"""
import json
import concurrent.futures
from typing import List, Dict
from backend.services.aws_integration import S3Client, TextractClient
from backend.database.dynamodb_client import DynamoDBClient
from backend.services.resume_parser.pdf_parser import PDFParser
from backend.services.resume_parser.skill_extractor import SkillExtractor
from backend.config import TEXTRACT_ENABLED


class BatchProcessor:
    """
    Handles batch processing of multiple resumes
    """
    
    def __init__(self, max_workers=5):
        """
        Initialize batch processor
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.s3_client = S3Client()
        self.pdf_parser = PDFParser()
        self.skill_extractor = SkillExtractor()
        self.db_client = DynamoDBClient()
        
        if TEXTRACT_ENABLED:
            self.textract_client = TextractClient()
        else:
            self.textract_client = None
    
    def process_resume(self, s3_key: str, bucket: str) -> Dict:
        """
        Process a single resume from S3
        Args:
            s3_key: S3 object key
            bucket: S3 bucket name
        Returns:
            Processing result dictionary
        """
        try:
            candidate_id = s3_key.split('/')[-1].replace('.pdf', '')
            
            # Extract text
            if self.textract_client:
                resume_text = self.textract_client.extract_text_from_s3(bucket, s3_key)
            else:
                local_path = f"/tmp/{candidate_id}.pdf"
                self.s3_client.download_resume(s3_key, local_path)
                resume_text = self.pdf_parser.extract_text_from_file(local_path)
            
            if not resume_text:
                return {
                    'candidate_id': candidate_id,
                    'status': 'failed',
                    'error': 'Text extraction failed'
                }
            
            # Extract skills and parse structure
            skills = self.skill_extractor.extract(resume_text)
            parsed_data = self.pdf_parser.parse_resume_structure(resume_text)
            
            # Store in DynamoDB
            candidate_record = {
                'candidate_id': candidate_id,
                's3_key': s3_key,
                'resume_text': resume_text,
                'skills': skills,
                'name': parsed_data.get('name', 'Unknown'),
                'email': parsed_data.get('email', ''),
                'phone': parsed_data.get('phone', ''),
                'experience_years': parsed_data.get('experience_years', 0),
                'education': parsed_data.get('education', ''),
                'status': 'processed'
            }
            
            self.db_client.put_candidate(candidate_record)
            
            return {
                'candidate_id': candidate_id,
                'status': 'success',
                'skills_found': len(skills)
            }
            
        except Exception as e:
            return {
                'candidate_id': s3_key,
                'status': 'failed',
                'error': str(e)
            }
    
    def process_batch(self, s3_keys: List[str], bucket: str) -> List[Dict]:
        """
        Process multiple resumes in parallel
        Args:
            s3_keys: List of S3 object keys
            bucket: S3 bucket name
        Returns:
            List of processing results
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_key = {
                executor.submit(self.process_resume, key, bucket): key 
                for key in s3_keys
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_key):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    key = future_to_key[future]
                    results.append({
                        'candidate_id': key,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        return results
    
    def get_batch_summary(self, results: List[Dict]) -> Dict:
        """
        Generate summary statistics for batch processing
        Args:
            results: List of processing results
        Returns:
            Summary dictionary
        """
        total = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = total - successful
        
        return {
            'total_processed': total,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful/total*100):.2f}%" if total > 0 else "0%"
        }
