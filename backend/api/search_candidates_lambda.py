"""
AWS Lambda handler for candidate search API
Integrates with: AWS Lambda, API Gateway, DynamoDB (future), S3 (future)
"""
import json
from backend.services.data_loader.dataset_loader import DatasetLoader
from backend.services.ranking_engine.ranker import Ranker
from backend.query_parser.query_parser import parse_query


def service(query):
    """
    Core service logic for candidate search
    Args:
        query: Job description or required skills string
    Returns:
        List of top 10 ranked candidates
    """
    # Load candidate data (will connect to DynamoDB in future)
    loader = DatasetLoader()
    candidates = loader.get_candidates()

    # Parse query to extract required skills
    skills = parse_query(query)

    # Rank candidates based on skill match and similarity
    ranker = Ranker()
    results = ranker.rank(candidates, skills)

    # Return top 10 candidates
    return results[:10]


def lambda_handler(event, context):
    """
    AWS Lambda entry point for API Gateway integration
    Args:
        event: API Gateway event with query parameter
        context: Lambda context object
    Returns:
        API Gateway response with ranked candidates
    """
    try:
        # Extract query from event (supports both body and queryStringParameters)
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
            query = body.get("query", "")
        else:
            query = event.get("queryStringParameters", {}).get("query", "") or event.get("query", "")

        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query parameter is required"}),
                "headers": {"Content-Type": "application/json"}
            }

        # Execute search service
        results = service(query)

        return {
            "statusCode": 200,
            "body": json.dumps({"results": results}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }