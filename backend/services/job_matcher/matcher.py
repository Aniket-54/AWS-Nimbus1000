"""
Skill matching engine for candidate screening
Calculates skill overlap between candidate and job requirements
"""
import ast


def skill_match(resume_skills, required_skills):
    """
    Calculate skill match score between candidate and job requirements
    Args:
        resume_skills: Candidate's skills (string or list)
        required_skills: Required skills from job description (list)
    Returns:
        Float score between 0 and 1 (percentage of required skills matched)
    Note:
        Future: Enhance with Amazon Bedrock for semantic skill matching
    """
    # Handle empty or None inputs
    if not resume_skills or not required_skills:
        return 0.0

    # Parse resume skills if stored as string representation of list
    if isinstance(resume_skills, str):
        try:
            # Try to parse as Python list literal (e.g., "['Python', 'Java']")
            resume_skills = ast.literal_eval(resume_skills)
        except (ValueError, SyntaxError):
            # If not a list literal, treat as comma-separated string
            resume_skills = resume_skills.split(",")
    
    # Convert to lowercase set for case-insensitive matching
    resume_set = set([s.lower().strip() for s in resume_skills if s])
    required_set = set([s.lower().strip() for s in required_skills if s])

    # Avoid division by zero
    if len(required_set) == 0:
        return 0.0

    # Calculate intersection (matched skills)
    intersection = resume_set.intersection(required_set)

    # Return match percentage
    return len(intersection) / len(required_set)