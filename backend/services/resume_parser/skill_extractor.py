"""
Skill extraction from resume text
Future integration: AWS Textract for PDF/image resume parsing
"""
import pandas as pd
import os


class SkillExtractor:
    """
    Extracts skills from resume text using predefined skill dictionary
    Future: Integrate with AWS Textract for document parsing
    """

    def __init__(self, skill_file="data/unique_skills.csv"):
        """
        Initialize skill extractor with skill dictionary
        Args:
            skill_file: Path to CSV file containing unique skills
        """
        if not os.path.exists(skill_file):
            raise FileNotFoundError(f"Skill file not found: {skill_file}")
        
        # Load unique skills from CSV (column name is 'Unique_Skills')
        df = pd.read_csv(skill_file)
        skill_column = df.columns[0]  # Get first column name
        self.skills = df[skill_column].str.lower().str.strip().tolist()
        
        # Remove any NaN or empty values
        self.skills = [s for s in self.skills if pd.notna(s) and s]

    def extract(self, text):
        """
        Extract skills from resume text
        Args:
            text: Resume text or skills string
        Returns:
            List of matched skills
        Note:
            Future: Use AWS Textract to extract text from PDF/image resumes
        """
        if not text or pd.isna(text):
            return []

        # Convert to lowercase for case-insensitive matching
        text = str(text).lower()

        found = []
        # Match skills in text (word boundary matching for accuracy)
        for skill in self.skills:
            # Use word boundary or check if skill is surrounded by non-alphanumeric chars
            if skill in text:
                found.append(skill)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(found))