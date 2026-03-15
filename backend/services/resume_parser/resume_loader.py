"""
Resume data loader
Future integration: AWS S3 for resume storage, AWS Textract for PDF parsing
"""
import pandas as pd
import os


class ResumeLoader:
    """
    Loads resume data from CSV file
    Future: Integrate with AWS S3 for resume storage and AWS Textract for PDF parsing
    """

    def __init__(self, path="data/resume_data.csv"):
        """
        Initialize resume loader with data path
        Args:
            path: Path to resume CSV file (future: S3 bucket path)
        """
        self.path = path
        self.data = None

    def load_resumes(self):
        """
        Load resume data from CSV file
        Returns:
            DataFrame containing resume data
        Note:
            Future: Load from S3 bucket using boto3
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Resume data file not found: {self.path}")
        
        self.data = pd.read_csv(self.path)
        return self.data

    def get_resume_by_id(self, serial_number):
        """
        Retrieve specific resume by serial number
        Args:
            serial_number: Unique identifier for resume
        Returns:
            Resume record as dictionary
        Note:
            Future: Query DynamoDB by candidate ID
        """
        if self.data is None:
            self.load_resumes()
        
        resume = self.data[self.data['Serial number'] == serial_number]
        if not resume.empty:
            return resume.iloc[0].to_dict()
        return None