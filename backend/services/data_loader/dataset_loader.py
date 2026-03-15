"""
Dataset loader for candidate data
Future integration: AWS DynamoDB for candidate database, S3 for data storage
"""
import pandas as pd
import os


class DatasetLoader:
    """
    Loads candidate dataset from CSV file
    Future: Replace with DynamoDB queries for scalable candidate retrieval
    """

    def __init__(self, path="data/resume_data.csv"):
        """
        Initialize dataset loader
        Args:
            path: Path to resume data CSV (future: DynamoDB table name)
        """
        self.path = path
        self.data = None

    def load(self):
        """
        Load candidate data from CSV file
        Returns:
            DataFrame with candidate information
        Note:
            Future: Use boto3 to query DynamoDB table
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Dataset file not found: {self.path}")
        
        self.data = pd.read_csv(self.path)
        return self.data

    def get_candidates(self):
        """
        Retrieve all candidates as list of dictionaries
        Returns:
            List of candidate records with skills, positions, responsibilities
        Note:
            Future: Implement pagination for large DynamoDB scans
        """
        if self.data is None:
            self.load()
        
        # Convert DataFrame to list of dictionaries for processing
        return self.data.to_dict(orient="records")