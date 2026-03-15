"""
API package for AWS Lambda handlers
Provides REST API endpoints for candidate search
"""
from .search_candidates_lambda import lambda_handler, service

__all__ = ['lambda_handler', 'service']
