"""
Embedding manager for RAG Assistant
Handles text embedding generation using Sentence Transformers
"""

from typing import List, Any
from langchain_huggingface import HuggingFaceEmbeddings
from ..config import Config


class EmbeddingManager:
    """Manages text embeddings using Sentence Transformers"""
    
    def __init__(self):
        """Initialize embedding manager with configured model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            raise Exception(f"Failed to initialize embeddings: {str(e)}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Integer representing embedding dimension
        """
        try:
            test_embedding = self.embed_text("test")
            return len(test_embedding)
        except Exception as e:
            raise Exception(f"Error getting embedding dimension: {str(e)}")
    
    def get_model_info(self) -> dict:
        """
        Get information about the embedding model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": Config.EMBEDDING_MODEL,
            "dimension": self.get_embedding_dimension(),
            "device": "cpu"
        }
