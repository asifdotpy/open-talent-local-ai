"""
Vector matching module for candidate-job semantic search.
Uses Neo4j vector database and sentence transformers for embeddings.
"""

from .models import CandidateEmbedding, JobEmbedding
from .service import VectorMatchingService
from .embeddings import EmbeddingGenerator

__all__ = [
    "CandidateEmbedding",
    "JobEmbedding",
    "VectorMatchingService",
    "EmbeddingGenerator",
]
