"""
Semantic similarity engine using NLP
Computes text similarity between job requirements and candidate experience
Future integration: Amazon Bedrock for advanced semantic understanding
"""
import spacy


# Load spaCy medium English model for semantic similarity
# Note: Requires 'python -m spacy download en_core_web_md'
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    # Fallback to small model if medium not available
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = None


def compute_similarity(text1, text2):
    """
    Compute semantic similarity between two text strings
    Args:
        text1: First text (e.g., candidate responsibilities)
        text2: Second text (e.g., job requirements)
    Returns:
        Float similarity score between 0 and 1
    Note:
        Future: Replace with Amazon Bedrock embeddings for better accuracy
    """
    # Handle None or empty inputs
    if not text1 or not text2:
        return 0.0
    
    # Check if spaCy model is loaded
    if nlp is None:
        # Fallback: Simple word overlap if spaCy not available
        words1 = set(str(text1).lower().split())
        words2 = set(str(text2).lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    # Convert to string and create spaCy documents
    doc1 = nlp(str(text1)[:1000000])  # Limit text length for performance
    doc2 = nlp(str(text2)[:1000000])

    # Compute cosine similarity between document vectors
    return doc1.similarity(doc2)