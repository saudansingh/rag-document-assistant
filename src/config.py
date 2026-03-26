"""
Configuration settings for RAG Document Assistant
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration constants"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Text Processing Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    SEPARATORS = ["\n\n", "\n", " ", ""]
    
    # Vector Database Configuration
    VECTOR_STORE_TYPE = "FAISS"
    RETRIEVAL_TOP_K = 5
    SIMILARITY_THRESHOLD = 0.0  # Lower threshold to get more results
    
    # LLM Configuration
    LLM_MODEL = "gemini-2.5-flash"
    LLM_TEMPERATURE = 0.1
    
    # File Upload Configuration
    SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'doc', 'txt']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # UI Configuration
    APP_TITLE = "Advanced RAG Document Assistant"
    APP_ICON = "📄"
    LAYOUT = "wide"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required in environment variables")
        
        return True
