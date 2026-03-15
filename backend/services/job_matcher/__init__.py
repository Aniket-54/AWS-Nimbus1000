"""
Job matcher service
Matches candidates to job requirements using skill matching and semantic similarity
"""
from .matcher import skill_match
from .similarity_engine import compute_similarity

__all__ = ['skill_match', 'compute_similarity']
