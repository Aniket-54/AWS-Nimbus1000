"""
DynamoDB client wrapper for candidate data operations
Future implementation for AWS DynamoDB integration
"""
import boto3
from botocore.exceptions import ClientError
from backend.config import AWS_REGION, DYNAMODB_TABLE_NAME, DYNAMODB_ENDPOINT


class DynamoDBClient:
    """
    DynamoDB client for candidate CRUD operations
    To be implemented when migrating from CSV to DynamoDB
    """

    def __init__(self):
        """
        Initialize DynamoDB client
        Uses environment variables for configuration
        """
        # Create DynamoDB resource
        if DYNAMODB_ENDPOINT:
            # For local DynamoDB testing
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION,
                endpoint_url=DYNAMODB_ENDPOINT
            )
        else:
            # For production AWS DynamoDB
            self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        
        self.table = self.dynamodb.Table(DYNAMODB_TABLE_NAME)

    def get_candidate(self, candidate_id):
        """
        Retrieve single candidate by ID
        Args:
            candidate_id: Unique candidate identifier
        Returns:
            Candidate record or None
        """
        try:
            response = self.table.get_item(Key={'candidate_id': candidate_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error retrieving candidate: {e}")
            return None

    def query_by_skill(self, skill, limit=100):
        """
        Query candidates by skill using GSI
        Args:
            skill: Skill to search for
            limit: Maximum number of results
        Returns:
            List of matching candidates
        """
        try:
            response = self.table.query(
                IndexName='SkillIndex',
                KeyConditionExpression='skill = :skill',
                ExpressionAttributeValues={':skill': skill},
                Limit=limit
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error querying by skill: {e}")
            return []

    def scan_all_candidates(self, limit=1000):
        """
        Scan all candidates (use with caution for large datasets)
        Args:
            limit: Maximum number of candidates to retrieve
        Returns:
            List of all candidate records
        """
        try:
            response = self.table.scan(Limit=limit)
            items = response.get('Items', [])
            
            # Handle pagination if more items exist
            while 'LastEvaluatedKey' in response and len(items) < limit:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    Limit=limit - len(items)
                )
                items.extend(response.get('Items', []))
            
            return items
        except ClientError as e:
            print(f"Error scanning candidates: {e}")
            return []

    def put_candidate(self, candidate_data):
        """
        Insert or update candidate record
        Args:
            candidate_data: Dictionary with candidate information
        Returns:
            True if successful, False otherwise
        """
        try:
            self.table.put_item(Item=candidate_data)
            return True
        except ClientError as e:
            print(f"Error putting candidate: {e}")
            return False

    def batch_write_candidates(self, candidates):
        """
        Batch insert multiple candidates
        Args:
            candidates: List of candidate dictionaries
        Returns:
            Number of successfully written items
        """
        success_count = 0
        
        # DynamoDB batch write supports max 25 items per batch
        batch_size = 25
        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i + batch_size]
            
            try:
                with self.table.batch_writer() as writer:
                    for candidate in batch:
                        writer.put_item(Item=candidate)
                        success_count += 1
            except ClientError as e:
                print(f"Error in batch write: {e}")
        
        return success_count
