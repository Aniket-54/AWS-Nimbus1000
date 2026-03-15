"""
Query parser to extract skills from job descriptions
Prepares for future integration with Amazon Bedrock for NLP enhancement
"""
import re


def parse_query(query):
    """
    Extract skills and keywords from job description query
    Args:
        query: Job description or requirements text
    Returns:
        List of extracted skill keywords
    Note:
        Future enhancement: Use Amazon Bedrock for advanced NLP parsing
    """
    if not query or not isinstance(query, str):
        return []

    # Convert to lowercase for consistent matching
    query = query.lower()

    # Extract alphanumeric words including special chars like C++, C#, .NET
    # Pattern matches: python, c++, c#, .net, node.js, etc.
    skills = re.findall(r"[a-zA-Z0-9]+[+#\.]*[a-zA-Z0-9]*", query)

    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        if skill and skill not in seen and len(skill) > 1:  # Filter single chars
            seen.add(skill)
            unique_skills.append(skill)

    return unique_skills