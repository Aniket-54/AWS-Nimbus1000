#!/usr/bin/env python3
"""
Script to migrate existing CSV data to DynamoDB
Run this once to populate DynamoDB with existing candidate data
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database.dynamodb_client import DynamoDBClient
from backend.services.resume_parser.skill_extractor import SkillExtractor


def migrate_csv_to_dynamodb(csv_path='data/resume_data.csv'):
    """
    Migrate candidate data from CSV to DynamoDB
    Args:
        csv_path: Path to CSV file
    """
    print(f"Loading data from {csv_path}...")
    
    # Load CSV
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} candidates in CSV")
    
    # Initialize clients
    db_client = DynamoDBClient()
    skill_extractor = SkillExtractor()
    
    # Prepare candidate records
    candidates = []
    for idx, row in df.iterrows():
        # Generate candidate_id from serial number or index
        candidate_id = str(row.get('Serial number', idx))
        
        # Extract skills if not already in proper format
        skills = row.get('Skills', [])
        if isinstance(skills, str):
            # Try to parse as list or extract from text
            try:
                skills = eval(skills) if skills.startswith('[') else skill_extractor.extract_skills(skills)
            except:
                skills = []
        
        candidate_record = {
            'candidate_id': candidate_id,
            'name': str(row.get('Name', 'Unknown')),
            'email': str(row.get('Email', '')),
            'phone': str(row.get('Phone', '')),
            'position': str(row.get('Position', '')),
            'skills': skills if isinstance(skills, list) else [],
            'resume_text': str(row.get('Resume', '')),
            'experience_years': int(row.get('Experience', 0)) if pd.notna(row.get('Experience')) else 0,
            'education': str(row.get('Education', '')),
            'upload_timestamp': datetime.utcnow().isoformat(),
            'status': 'migrated',
            's3_key': ''  # Empty for migrated records
        }
        
        candidates.append(candidate_record)
        
        # Print progress
        if (idx + 1) % 10 == 0:
            print(f"Prepared {idx + 1}/{len(df)} records...")
    
    # Batch write to DynamoDB
    print("\nWriting to DynamoDB...")
    success_count = db_client.batch_write_candidates(candidates)
    
    print(f"\nMigration complete!")
    print(f"Successfully migrated {success_count}/{len(candidates)} candidates")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate CSV data to DynamoDB')
    parser.add_argument('--csv', default='data/resume_data.csv', help='Path to CSV file')
    
    args = parser.parse_args()
    
    try:
        migrate_csv_to_dynamodb(args.csv)
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)
