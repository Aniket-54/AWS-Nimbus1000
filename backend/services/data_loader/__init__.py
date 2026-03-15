"""
Data loader service
Loads candidate data from CSV (future: DynamoDB)
"""
from .dataset_loader import DatasetLoader

__all__ = ['DatasetLoader']
