"""
Document uploader component for RAG Assistant
Handles file upload and processing interface
"""

import streamlit as st
import tempfile
from typing import List, Dict, Any
from ..config import Config
from ..document_processors import DocumentProcessor


class DocumentUploader:
    """Document upload and processing interface"""
    
    def __init__(self):
        """Initialize document uploader"""
        self.custom_css = self._get_custom_css()
        self.document_processor = DocumentProcessor()
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for document uploader"""
        return """
        <style>
            .upload-area {
                border: 2px dashed #4285f4;
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
                background: #f8f9fa;
                margin: 1rem 0;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                border-color: #34a853;
                background: #f0f8f0;
            }
            .status-card {
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                border-left: 4px solid #4285f4;
                background: #e8f0fe;
            }
            .status-success {
                border-left-color: #34a853;
                background: #e8f5e8;
            }
            .status-error {
                border-left-color: #ea4335;
                background: #ffebee;
            }
            .status-warning {
                border-left-color: #fbbc04;
                background: #fff8e1;
            }
            .file-info {
                font-size: 0.9rem;
                color: #666;
                margin: 0.5rem 0;
            }
            .processing-spinner {
                text-align: center;
                padding: 2rem;
            }
        </style>
        """
    
    def apply_custom_css(self):
        """Apply custom CSS"""
        st.markdown(self.custom_css, unsafe_allow_html=True)
    
    def display_upload_interface(self) -> List:
        """
        Display simple file upload interface
        
        Returns:
            List of uploaded files
        """
        uploaded_files = st.file_uploader(
            "Choose documents",
            type=Config.SUPPORTED_FILE_TYPES,
            accept_multiple_files=True,
            key="document_uploader"
        )
        
        return uploaded_files
    
    def _display_file_info(self, uploaded_files: List):
        """
        Display information about uploaded files
        
        Args:
            uploaded_files: List of uploaded files
        """
        st.markdown("### 📋 File Information")
        
        for file in uploaded_files:
            file_info = self.document_processor.get_file_info(file)
            
            if file_info["supported"]:
                st.markdown(f"""
                <div class="status-card status-success">
                    <strong>✅ {file_info["name"]}</strong><br>
                    <span class="file-info">
                        Type: {file_info["type"].upper()} | Size: {file_info["size"]:,} bytes
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-card status-error">
                    <strong>❌ {file_info["name"]}</strong><br>
                    <span class="file-info">
                        Unsupported file type: {file_info["type"].upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    def display_processing_button(self, uploaded_files: List) -> bool:
        """
        Display simple processing button
        
        Args:
            uploaded_files: List of uploaded files
            
        Returns:
            Whether processing was requested
        """
        if not uploaded_files:
            return False
        
        return st.button(
            "Process Documents", 
            type="primary", 
            use_container_width=True
        )
    
    def process_documents(self, uploaded_files: List) -> tuple:
        """
        Process uploaded documents
        
        Args:
            uploaded_files: List of uploaded files
            
        Returns:
            Tuple of (documents, document_info)
        """
        if not uploaded_files:
            return [], {}
        
        all_documents = []
        document_info = {}
        processing_errors = []
        
        with st.spinner("📄 Processing documents..."):
            for uploaded_file in uploaded_files:
                try:
                    st.write(f"Processing: {uploaded_file.name}")
                    
                    # Process document
                    documents = self.document_processor.process_document(uploaded_file)
                    all_documents.extend(documents)
                    
                    # Store document info
                    document_info[uploaded_file.name] = {
                        "chunks": len(documents),
                        "size": len(uploaded_file.getvalue()),
                        "type": uploaded_file.name.split('.')[-1].upper(),
                        "status": "success"
                    }
                    
                    st.success(f"✅ {uploaded_file.name}: {len(documents)} chunks created")
                    
                except Exception as e:
                    error_msg = f"Error processing {uploaded_file.name}: {str(e)}"
                    processing_errors.append(error_msg)
                    document_info[uploaded_file.name] = {
                        "chunks": 0,
                        "size": len(uploaded_file.getvalue()),
                        "type": uploaded_file.name.split('.')[-1].upper(),
                        "status": "error",
                        "error": str(e)
                    }
                    st.error(f"❌ {error_msg}")
        
        return all_documents, document_info, processing_errors
    
    def display_processing_results(self, document_info: Dict[str, Any], 
                                 processing_errors: List[str]):
        """
        Display processing results
        
        Args:
            document_info: Information about processed documents
            processing_errors: List of processing errors
        """
        if processing_errors:
            st.error("### ❌ Processing Errors")
            for error in processing_errors:
                st.error(error)
        
        if document_info:
            st.markdown("### 📊 Processing Results")
            
            total_docs = len(document_info)
            successful_docs = sum(1 for info in document_info.values() if info["status"] == "success")
            total_chunks = sum(info["chunks"] for info in document_info.values())
            total_size = sum(info["size"] for info in document_info.values())
            
            st.markdown(f"""
            <div class="status-card status-success">
                <strong>✅ Processing Summary</strong><br>
                Documents: {successful_docs}/{total_docs} successful<br>
                Total Chunks: {total_chunks:,}<br>
                Total Size: {total_size:,} bytes
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed document info
            for doc_name, info in document_info.items():
                status_emoji = "✅" if info["status"] == "success" else "❌"
                st.markdown(f"""
                <div class="status-card">
                    <strong>{status_emoji} {doc_name}</strong><br>
                    Type: {info['type']} | Chunks: {info['chunks']} | Size: {info['size']:,} bytes
                </div>
                """, unsafe_allow_html=True)
    
    def get_supported_file_types(self) -> str:
        """Get formatted string of supported file types"""
        return ", ".join([f".{ext.upper()}" for ext in Config.SUPPORTED_FILE_TYPES])
    
    def display_file_type_info(self):
        """Display information about supported file types"""
        with st.expander("📖 Supported File Types"):
            st.markdown("""
            **PDF Files (.pdf)**
            - Uses PyMuPDF for text extraction
            - Preserves page numbers and metadata
            - Handles multi-page documents
            
            **Word Documents (.docx, .doc)**
            - Uses python-docx for text extraction
            - Extracts paragraphs and tables
            - Preserves document structure
            
            **Text Files (.txt, .text, .md)**
            - Supports UTF-8 and Latin-1 encoding
            - Handles plain text and markdown
            - Preserves line breaks and paragraphs
            """)
