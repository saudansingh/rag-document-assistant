"""
Vector store module for RAG Assistant
Handles embedding generation and vector storage
"""

from .embedding_manager import EmbeddingManager
from .vector_store_manager import VectorStoreManager

__all__ = [
    'EmbeddingManager',
    'VectorStoreManager'
]
