"""
Dataset loader for candidate data
Supports both CSV (local) and DynamoDB (production) data sources
"""
import pandas as pd
import os
from backend.config import DYNAMODB_TABLE_NAME


class DatasetLoader:
    """
    Loads candidate dataset from CSV file or DynamoDB
    Automatically switches based on environment configuration
    """

    def __init__(self, path="data/resume_data.csv", use_dynamodb=False):
        """
        Initialize dataset loader
        Args:
            path: Path to resume data CSV (for local development)
            use_dynamodb: If True, load from DynamoDB instead of CSV
        """
        self.path = path
        self.data = None
        self.use_dynamodb = use_dynamodb or os.environ.get('USE_DYNAMODB', 'false').lower() == 'true'

    def load(self):
        """
        Load candidate data from CSV file or DynamoDB
        Returns:
            DataFrame with candidate information
        """
        if self.use_dynamodb:
            return self._load_from_dynamodb()
        else:
            return self._load_from_csv()
    
    def _load_from_csv(self):
        """Load from local CSV file"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Dataset file not found: {self.path}")
        
        self.data = pd.read_csv(self.path)
        return self.data
    
    def _load_from_dynamodb(self):
        """Load from DynamoDB table"""
        try:
            from backend.database.dynamodb_client import DynamoDBClient
            db_client = DynamoDBClient()
            candidates = db_client.scan_all_candidates()
            self.data = pd.DataFrame(candidates)
            return self.data
        except Exception as e:
            print(f"Error loading from DynamoDB: {e}")
            print("Falling back to CSV...")
            return self._load_from_csv()

    def get_candidates(self):
        """
        Retrieve all candidates as list of dictionaries
        Returns:
            List of candidate records with skills, positions, responsibilities
        """
        if self.data is None:
            self.load()
        
        # Convert DataFrame to list of dictionaries for processing
        return self.data.to_dict(orient="records")