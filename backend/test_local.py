"""
Local testing script for recruitment assistant backend
Tests all components without AWS services
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api.search_candidates_lambda import service, lambda_handler
from backend.services.data_loader.dataset_loader import DatasetLoader
from backend.query_parser.query_parser import parse_query
from backend.services.job_matcher.matcher import skill_match
from backend.services.job_matcher.similarity_engine import compute_similarity
from backend.services.ranking_engine.ranker import Ranker


def test_query_parser():
    """Test query parsing functionality"""
    print("\n=== Testing Query Parser ===")
    query = "Looking for Python developer with machine learning and AWS experience"
    skills = parse_query(query)
    print(f"Query: {query}")
    print(f"Extracted skills: {skills}")
    assert len(skills) > 0, "Should extract at least one skill"
    print("✓ Query parser test passed")


def test_dataset_loader():
    """Test dataset loading"""
    print("\n=== Testing Dataset Loader ===")
    loader = DatasetLoader()
    candidates = loader.get_candidates()
    print(f"Loaded {len(candidates)} candidates")
    if candidates:
        print(f"Sample candidate keys: {list(candidates[0].keys())}")
    assert len(candidates) > 0, "Should load candidates"
    print("✓ Dataset loader test passed")


def test_skill_match():
    """Test skill matching"""
    print("\n=== Testing Skill Matcher ===")
    resume_skills = "['Python', 'Java', 'Machine Learning', 'AWS']"
    required_skills = ["python", "aws", "docker"]
    score = skill_match(resume_skills, required_skills)
    print(f"Resume skills: {resume_skills}")
    print(f"Required skills: {required_skills}")
    print(f"Match score: {score:.2f}")
    assert 0 <= score <= 1, "Score should be between 0 and 1"
    print("✓ Skill matcher test passed")


def test_similarity_engine():
    """Test semantic similarity"""
    print("\n=== Testing Similarity Engine ===")
    text1 = "Developed machine learning models using Python and TensorFlow"
    text2 = "Python machine learning experience"
    score = compute_similarity(text1, text2)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity score: {score:.2f}")
    assert 0 <= score <= 1, "Score should be between 0 and 1"
    print("✓ Similarity engine test passed")


def test_ranker():
    """Test ranking engine"""
    print("\n=== Testing Ranker ===")
    candidates = [
        {
            "Serial number": 1,
            "skills": "['Python', 'Machine Learning', 'AWS']",
            "responsibilities": "Developed ML models and deployed on AWS"
        },
        {
            "Serial number": 2,
            "skills": "['Java', 'Spring Boot']",
            "responsibilities": "Built enterprise applications"
        }
    ]
    query_skills = ["python", "machine", "learning"]
    ranker = Ranker()
    results = ranker.rank(candidates, query_skills)
    print(f"Ranked {len(results)} candidates")
    for i, candidate in enumerate(results[:2], 1):
        print(f"{i}. Score: {candidate['score']:.2f}, Skills: {candidate.get('skills', 'N/A')[:50]}")
    assert results[0]['score'] >= results[1]['score'], "Results should be sorted by score"
    print("✓ Ranker test passed")


def test_service():
    """Test main service function"""
    print("\n=== Testing Main Service ===")
    query = "Python developer with machine learning experience"
    results = service(query)
    print(f"Query: {query}")
    print(f"Found {len(results)} top candidates")
    if results:
        print(f"Top candidate score: {results[0].get('score', 0):.2f}")
    assert len(results) <= 10, "Should return max 10 results"
    print("✓ Service test passed")


def test_lambda_handler():
    """Test Lambda handler"""
    print("\n=== Testing Lambda Handler ===")
    
    # Test with body
    event = {
        "body": '{"query": "Python AWS developer"}'
    }
    response = lambda_handler(event, None)
    print(f"Status code: {response['statusCode']}")
    assert response['statusCode'] == 200, "Should return 200 status"
    print("✓ Lambda handler test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RECRUITMENT ASSISTANT BACKEND - LOCAL TESTS")
    print("=" * 60)
    
    try:
        test_query_parser()
        test_dataset_loader()
        test_skill_match()
        test_similarity_engine()
        test_ranker()
        test_service()
        test_lambda_handler()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
