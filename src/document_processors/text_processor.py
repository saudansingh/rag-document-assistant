"""
Text document processor
Extracts text and metadata from plain text files
"""

import os
from datetime import datetime
from typing import List, Dict, Any


class TextProcessor:
    """Handles plain text file extraction with metadata"""
    
    def __init__(self):
        self.supported_extensions = ['txt', 'text', 'md']
    
    def extract_text_from_text(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from plain text file with metadata
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of dictionaries containing text content and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # File metadata
            file_stats = os.stat(file_path)
            doc_metadata = {
                "source": file_path,
                "file_type": "txt",
                "processed_at": datetime.now().isoformat(),
                "file_size": file_stats.st_size,
                "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "encoding": "utf-8",
                "lines_count": len(content.splitlines()),
                "characters_count": len(content),
                "words_count": len(content.split())
            }
            
            # Split into paragraphs for better chunking
            paragraphs = content.split('\n\n')
            text_content = []
            
            for para_num, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    para_metadata = doc_metadata.copy()
                    para_metadata.update({
                        "paragraph_number": para_num + 1,
                        "paragraph_size": len(paragraph.strip()),
                        "content_type": "paragraph"
                    })
                    
                    text_content.append({
                        "content": paragraph.strip(),
                        "metadata": para_metadata
                    })
            
            return text_content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                
                file_stats = os.stat(file_path)
                doc_metadata = {
                    "source": file_path,
                    "file_type": "txt",
                    "processed_at": datetime.now().isoformat(),
                    "file_size": file_stats.st_size,
                    "encoding": "latin-1"
                }
                
                return [{
                    "content": content,
                    "metadata": doc_metadata
                }]
                
            except Exception as e:
                raise Exception(f"Error reading text file with encoding: {str(e)}")
                
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from text file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary containing text file metadata
        """
        try:
            file_stats = os.stat(file_path)
            
            return {
                "file_size": file_stats.st_size,
                "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "encoding": "utf-8"
            }
            
        except Exception as e:
            raise Exception(f"Error extracting text metadata: {str(e)}")
    
    def is_supported(self, file_extension: str) -> bool:
        """Check if file extension is supported"""
        return file_extension.lower() in self.supported_extensions
