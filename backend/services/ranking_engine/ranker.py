"""
Candidate ranking engine
Scores and ranks candidates based on skill match and semantic similarity
"""
from backend.services.job_matcher.matcher import skill_match
from backend.services.job_matcher.similarity_engine import compute_similarity


class Ranker:
    """
    Ranks candidates based on job requirements
    Combines skill matching and semantic similarity for comprehensive scoring
    """

    def __init__(self, skill_weight=0.6, similarity_weight=0.4):
        """
        Initialize ranker with scoring weights
        Args:
            skill_weight: Weight for exact skill match (default 0.6)
            similarity_weight: Weight for semantic similarity (default 0.4)
        """
        self.skill_weight = skill_weight
        self.similarity_weight = similarity_weight

    def rank(self, candidates, query_skills):
        """
        Rank candidates based on job requirements
        Args:
            candidates: List of candidate dictionaries from dataset
            query_skills: List of required skills extracted from job description
        Returns:
            List of candidates sorted by score (highest first)
        Note:
            Future: Store ranking results in DynamoDB for analytics
        """
        scored = []

        for candidate in candidates:
            # Calculate exact skill match score (0-1)
            skill_score = skill_match(
                candidate.get("skills", ""),
                query_skills
            )

            # Calculate semantic similarity between responsibilities and requirements
            sim_score = compute_similarity(
                candidate.get("responsibilities", ""),
                " ".join(query_skills)
            )

            # Weighted combination of skill match and semantic similarity
            final_score = (
                self.skill_weight * skill_score +
                self.similarity_weight * sim_score
            )

            # Add score to candidate record
            candidate["score"] = round(final_score, 4)
            candidate["skill_match"] = round(skill_score, 4)
            candidate["similarity_score"] = round(sim_score, 4)

            scored.append(candidate)

        # Sort candidates by final score in descending order
        ranked = sorted(scored, key=lambda x: x["score"], reverse=True)

        return ranked