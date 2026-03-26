"""
Main document processor that orchestrates all document type processors
"""

import uuid
import tempfile
import os
from typing import List, Dict, Any
from langchain_core.documents import Document

from .pdf_processor import PDFProcessor
from .docx_processor import DocxProcessor
from .text_processor import TextProcessor
from ..config import Config


class DocumentProcessor:
    """Main document processor that handles multiple document types"""
    
    def __init__(self):
        self.processors = {
            'pdf': PDFProcessor(),
            'docx': DocxProcessor(),
            'doc': DocxProcessor(),
            'txt': TextProcessor(),
            'text': TextProcessor(),
            'md': TextProcessor()
        }
        
        # Initialize text splitter (will be moved to separate module later)
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=Config.SEPARATORS
        )
    
    def process_document(self, uploaded_file) -> List[Document]:
        """
        Process uploaded document and return chunks with metadata
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            List of Document objects with chunks and metadata
        """
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Get file extension
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            # Get appropriate processor
            processor = self.processors.get(file_extension)
            if not processor:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Extract text content
            if file_extension == 'pdf':
                text_content = processor.extract_text_from_pdf(tmp_file_path)
            elif file_extension in ['docx', 'doc']:
                text_content = processor.extract_text_from_docx(tmp_file_path)
            elif file_extension in ['txt', 'text', 'md']:
                text_content = processor.extract_text_from_text(tmp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Create documents with chunks and metadata
            documents = []
            chunk_id = 0
            
            for content_item in text_content:
                chunks = self.text_splitter.split_text(content_item["content"])
                
                for chunk in chunks:
                    chunk_metadata = content_item["metadata"].copy()
                    chunk_metadata.update({
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_index": chunk_id,
                        "chunk_size": len(chunk),
                        "original_file": uploaded_file.name,
                        "processing_timestamp": Config.validate_config()
                    })
                    
                    doc = Document(
                        page_content=chunk,
                        metadata=chunk_metadata
                    )
                    documents.append(doc)
                    chunk_id += 1
            
            return documents
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file extensions"""
        return list(self.processors.keys())
    
    def is_supported(self, file_name: str) -> bool:
        """Check if file type is supported"""
        extension = file_name.lower().split('.')[-1]
        return extension in self.processors
    
    def get_file_info(self, uploaded_file) -> Dict[str, Any]:
        """
        Get basic information about uploaded file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Dictionary with file information
        """
        return {
            "name": uploaded_file.name,
            "size": len(uploaded_file.getvalue()),
            "type": uploaded_file.name.lower().split('.')[-1],
            "supported": self.is_supported(uploaded_file.name)
        }
