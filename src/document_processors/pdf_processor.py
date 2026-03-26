"""
PDF document processor using PyMuPDF
Extracts text and metadata from PDF files
"""

import fitz  # PyMuPDF
from datetime import datetime
from typing import List, Dict, Any
import tempfile
import os


class PDFProcessor:
    """Handles PDF text extraction with metadata using PyMuPDF"""
    
    def __init__(self):
        self.supported_extensions = ['pdf']
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF file with rich metadata
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing text content and metadata
        """
        try:
            doc = fitz.open(file_path)
            text_content = []
            
            # Document-level metadata
            doc_metadata = {
                "source": file_path,
                "total_pages": len(doc),
                "file_type": "pdf",
                "processed_at": datetime.now().isoformat(),
                "title": doc.metadata.get('title', ''),
                "author": doc.metadata.get('author', ''),
                "subject": doc.metadata.get('subject', '')
            }
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                if page_text.strip():
                    # Page-specific metadata
                    page_metadata = doc_metadata.copy()
                    page_metadata.update({
                        "page_number": page_num + 1,
                        "page_size": len(page_text),
                        "rotation": page.rotation,
                        "rect": page.rect
                    })
                    
                    text_content.append({
                        "content": page_text,
                        "metadata": page_metadata
                    })
            
            doc.close()
            return text_content
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            doc.close()
            
            return {
                "title": metadata.get('title', ''),
                "author": metadata.get('author', ''),
                "subject": metadata.get('subject', ''),
                "creator": metadata.get('creator', ''),
                "producer": metadata.get('producer', ''),
                "creation_date": metadata.get('creationDate', ''),
                "modification_date": metadata.get('modDate', ''),
                "total_pages": len(fitz.open(file_path))
            }
            
        except Exception as e:
            raise Exception(f"Error extracting PDF metadata: {str(e)}")
    
    def is_supported(self, file_extension: str) -> bool:
        """Check if file extension is supported"""
        return file_extension.lower() in self.supported_extensions
