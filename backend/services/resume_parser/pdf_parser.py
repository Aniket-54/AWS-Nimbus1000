"""
PDF parsing utilities for resume extraction
Supports both local parsing and AWS Textract integration
"""
import re
import io
import PyPDF2
import pdfplumber


class PDFParser:
    """
    Extracts text and structured data from PDF resumes
    """
    
    def extract_text_from_file(self, file_path):
        """
        Extract text from PDF file using pdfplumber (better for complex layouts)
        Args:
            file_path: Path to PDF file
        Returns:
            Extracted text string
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            return self._extract_with_pypdf2(file_path)
    
    def extract_text_from_bytes(self, pdf_bytes):
        """
        Extract text from PDF bytes (for Lambda uploads)
        Args:
            pdf_bytes: PDF file content as bytes
        Returns:
            Extracted text string
        """
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            return self._extract_bytes_with_pypdf2(pdf_bytes)
    
    def _extract_with_pypdf2(self, file_path):
        """
        Fallback extraction using PyPDF2
        Args:
            file_path: Path to PDF file
        Returns:
            Extracted text string
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def _extract_bytes_with_pypdf2(self, pdf_bytes):
        """
        Fallback extraction from bytes using PyPDF2
        Args:
            pdf_bytes: PDF content as bytes
        Returns:
            Extracted text string
        """
        try:
            text = ""
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def parse_resume_structure(self, text):
        """
        Extract structured information from resume text
        Args:
            text: Resume text content
        Returns:
            Dictionary with parsed fields (name, email, phone, etc.)
        """
        parsed = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(text)
        }
        return parsed
    
    def _extract_name(self, text):
        """Extract candidate name (usually first line)"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 50 and not '@' in line:
                # Simple heuristic: name is usually short and at the top
                return line
        return "Unknown"
    
    def _extract_email(self, text):
        """Extract email address using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text):
        """Extract phone number using regex"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    def _extract_experience_years(self, text):
        """Estimate years of experience from text"""
        # Look for patterns like "5 years", "5+ years", "5-7 years"
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
    
    def _extract_education(self, text):
        """Extract education information"""
        education_keywords = ['bachelor', 'master', 'phd', 'mba', 'degree', 'university', 'college']
        lines = text.lower().split('\n')
        education_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in education_keywords):
                education_lines.append(line.strip())
        
        return ' | '.join(education_lines[:3]) if education_lines else ""
