"""
Resume parser service
Extracts skills and loads resume data (future: AWS Textract integration)
"""
from .resume_loader import ResumeLoader
from .skill_extractor import SkillExtractor

__all__ = ['ResumeLoader', 'SkillExtractor']
