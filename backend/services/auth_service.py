"""
Authentication service for HR users
Future integration with AWS Cognito for user management
"""
import boto3
from botocore.exceptions import ClientError
from backend.config import AWS_REGION, COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID


class CognitoAuthService:
    """
    AWS Cognito authentication service
    Manages HR user authentication and authorization
    """

    def __init__(self):
        """Initialize Cognito client"""
        self.cognito = boto3.client('cognito-idp', region_name=AWS_REGION)
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID

    def authenticate_user(self, username, password):
        """
        Authenticate HR user with Cognito
        Args:
            username: User email or username
            password: User password
        Returns:
            Authentication tokens if successful, None otherwise
        """
        try:
            response = self.cognito.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            return response.get('AuthenticationResult')
        except ClientError as e:
            print(f"Authentication error: {e}")
            return None

    def verify_token(self, access_token):
        """
        Verify JWT access token
        Args:
            access_token: JWT token from client
        Returns:
            User information if valid, None otherwise
        """
        try:
            response = self.cognito.get_user(AccessToken=access_token)
            return {
                'username': response['Username'],
                'attributes': {
                    attr['Name']: attr['Value']
                    for attr in response['UserAttributes']
                }
            }
        except ClientError as e:
            print(f"Token verification error: {e}")
            return None

    def create_hr_user(self, email, temporary_password, full_name):
        """
        Create new HR user in Cognito
        Args:
            email: User email address
            temporary_password: Temporary password (user must change on first login)
            full_name: User's full name
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'name', 'Value': full_name}
                ],
                TemporaryPassword=temporary_password,
                MessageAction='SUPPRESS'  # Don't send email (handle manually)
            )
            return True
        except ClientError as e:
            print(f"Error creating user: {e}")
            return False

    def reset_password(self, username):
        """
        Initiate password reset for user
        Args:
            username: User email or username
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cognito.admin_reset_user_password(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return True
        except ClientError as e:
            print(f"Error resetting password: {e}")
            return False

    def list_hr_users(self):
        """
        List all HR users in Cognito pool
        Returns:
            List of user records
        """
        try:
            response = self.cognito.list_users(UserPoolId=self.user_pool_id)
            return response.get('Users', [])
        except ClientError as e:
            print(f"Error listing users: {e}")
            return []


def require_auth(func):
    """
    Decorator to require authentication for Lambda functions
    Usage:
        @require_auth
        def lambda_handler(event, context):
            # Function code
    """
    def wrapper(event, context):
        # Extract token from Authorization header
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401,
                'body': '{"error": "Missing or invalid authorization header"}',
                'headers': {'Content-Type': 'application/json'}
            }
        
        token = auth_header.replace('Bearer ', '')
        
        # Verify token
        auth_service = CognitoAuthService()
        user_info = auth_service.verify_token(token)
        
        if not user_info:
            return {
                'statusCode': 401,
                'body': '{"error": "Invalid or expired token"}',
                'headers': {'Content-Type': 'application/json'}
            }
        
        # Add user info to event for use in function
        event['user'] = user_info
        
        # Call original function
        return func(event, context)
    
    return wrapper
