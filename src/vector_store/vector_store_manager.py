"""
Vector store manager for RAG Assistant
Handles FAISS vector storage and retrieval operations
"""

from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .embedding_manager import EmbeddingManager
from ..config import Config


class VectorStoreManager:
    """Manages FAISS vector store operations"""
    
    def __init__(self):
        """Initialize vector store manager"""
        self.embedding_manager = EmbeddingManager()
        self.vector_store: Optional[FAISS] = None
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create FAISS vector store from documents
        
        Args:
            documents: List of Document objects
            
        Returns:
            FAISS vector store instance
        """
        try:
            if not documents:
                raise ValueError("No documents provided to create vector store")
            
            # Create vector store
            self.vector_store = FAISS.from_documents(
                documents, 
                self.embedding_manager.embeddings
            )
            
            return self.vector_store
            
        except Exception as e:
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vector store
        
        Args:
            documents: List of Document objects to add
        """
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            if not documents:
                raise ValueError("No documents to add")
            
            self.vector_store.add_documents(documents)
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    def similarity_search(self, query: str, k: int = Config.RETRIEVAL_TOP_K) -> List[Document]:
        """
        Perform similarity search on vector store
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            return self.vector_store.similarity_search(query, k=k)
            
        except Exception as e:
            raise Exception(f"Error performing similarity search: {str(e)}")
    
    def similarity_search_with_score(self, query: str, k: int = Config.RETRIEVAL_TOP_K) -> List[tuple]:
        """
        Perform similarity search with scores
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of (Document, score) tuples
        """
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            return self.vector_store.similarity_search_with_score(query, k=k)
            
        except Exception as e:
            raise Exception(f"Error performing similarity search with scores: {str(e)}")
    
    def get_retriever(self):
        """
        Get retriever from vector store
        
        Returns:
            Retriever object for RAG pipeline
        """
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": Config.RETRIEVAL_TOP_K}
            )
            
        except Exception as e:
            raise Exception(f"Error creating retriever: {str(e)}")
    
    def save_vector_store(self, file_path: str) -> None:
        """
        Save vector store to disk
        
        Args:
            file_path: Path to save vector store
        """
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            self.vector_store.save_local(file_path)
            
        except Exception as e:
            raise Exception(f"Error saving vector store: {str(e)}")
    
    def load_vector_store(self, file_path: str) -> FAISS:
        """
        Load vector store from disk
        
        Args:
            file_path: Path to load vector store from
            
        Returns:
            Loaded FAISS vector store
        """
        try:
            self.vector_store = FAISS.load_local(
                file_path, 
                self.embedding_manager.embeddings,
                allow_dangerous_deserialization=True
            )
            return self.vector_store
            
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store
        
        Returns:
            Dictionary with vector store information
        """
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        try:
            # Get basic info
            index_info = {
                "status": "initialized",
                "embedding_model": self.embedding_manager.get_model_info(),
                "index_type": "FAISS",
                "retrieval_config": {
                    "top_k": Config.RETRIEVAL_TOP_K,
                    "similarity_threshold": Config.SIMILARITY_THRESHOLD
                }
            }
            
            return index_info
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
