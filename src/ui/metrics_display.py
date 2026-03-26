"""
Metrics display component for RAG Assistant
Displays real-time processing metrics and system information
"""

import streamlit as st
from typing import Dict, Any, List
from ..config import Config


class MetricsDisplay:
    """Display metrics and system information"""
    
    def __init__(self):
        """Initialize metrics display"""
        self.custom_css = self._get_custom_css()
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for metrics display"""
        return """
        <style>
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 1rem 0;
            }
            .metric-card {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-2px);
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #4285f4;
                margin-bottom: 0.5rem;
            }
            .metric-label {
                color: #666;
                font-size: 0.9rem;
                margin-bottom: 0.25rem;
            }
            .metric-sublabel {
                color: #999;
                font-size: 0.8rem;
            }
            .system-info {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #4285f4;
                margin: 1rem 0;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 0.5rem;
            }
            .status-ready {
                background: #34a853;
            }
            .status-processing {
                background: #fbbc04;
            }
            .status-error {
                background: #ea4335;
            }
        </style>
        """
    
    def apply_custom_css(self):
        """Apply custom CSS"""
        st.markdown(self.custom_css, unsafe_allow_html=True)
    
    def display_processing_metrics(self, document_info: Dict[str, Any]):
        """
        Display document processing metrics
        
        Args:
            document_info: Information about processed documents
        """
        if not document_info:
            return
        
        # Calculate metrics
        total_documents = len(document_info)
        total_chunks = sum(info["chunks"] for info in document_info.values())
        total_size = sum(info["size"] for info in document_info.values())
        successful_docs = sum(1 for info in document_info.values() if info["status"] == "success")
        
        # Display metrics grid
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        # Documents metric
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_documents}</div>
            <div class="metric-label">Documents</div>
            <div class="metric-sublabel">{successful_docs} successful</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chunks metric
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_chunks:,}</div>
            <div class="metric-label">Text Chunks</div>
            <div class="metric-sublabel">Ready for search</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Size metric
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{self._format_size(total_size)}</div>
            <div class="metric-label">Total Size</div>
            <div class="metric-sublabel">All documents</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Success rate metric
        success_rate = (successful_docs / total_documents * 100) if total_documents > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{success_rate:.1f}%</div>
            <div class="metric-label">Success Rate</div>
            <div class="metric-sublabel">Processing</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_system_info(self, rag_assistant=None, vector_store_manager=None):
        """
        Display system information
        
        Args:
            rag_assistant: RAG assistant instance
            vector_store_manager: Vector store manager instance
        """
        st.markdown("### 🔧 System Information")
        
        # RAG system info
        if rag_assistant:
            system_info = rag_assistant.get_system_info()
            
            st.markdown('<div class="system-info">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="status-indicator status-ready"></div>
            <strong>LLM Model:</strong> {system_info["llm_model"]}<br>
            <strong>Temperature:</strong> {system_info["llm_temperature"]}<br>
            <strong>Retrieval Top-K:</strong> {system_info["retrieval_config"]["top_k"]}<br>
            <strong>Similarity Threshold:</strong> {system_info["retrieval_config"]["similarity_threshold"]}
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Vector store info
        if vector_store_manager:
            vector_info = vector_store_manager.get_vector_store_info()
            
            st.markdown('<div class="system-info">', unsafe_allow_html=True)
            
            if vector_info["status"] == "initialized":
                st.markdown(f"""
                <div class="status-indicator status-ready"></div>
                <strong>Vector Store:</strong> {vector_info["index_type"]}<br>
                <strong>Embedding Model:</strong> {vector_info["embedding_model"]["model_name"]}<br>
                <strong>Embedding Dimension:</strong> {vector_info["embedding_model"]["dimension"]}<br>
                <strong>Device:</strong> {vector_info["embedding_model"]["device"]}
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-indicator status-error"></div>
                <strong>Vector Store:</strong> Not initialized
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def display_configuration_info(self):
        """Display configuration information"""
        with st.expander("⚙️ Configuration Details"):
            st.markdown("""
            **Text Processing**
            - Chunk Size: 1000 characters
            - Chunk Overlap: 200 characters
            - Separators: Paragraphs, lines, spaces
            
            **Vector Search**
            - Similarity Algorithm: FAISS
            - Retrieval Method: Similarity Score Threshold
            - Top-K Results: 5
            - Minimum Similarity: 0.3
            
            **LLM Configuration**
            - Model: Gemini 1.5 Pro
            - Temperature: 0.1 (for consistency)
            - Max Tokens: Default
            """)
    
    def display_performance_metrics(self, query_history: List[Dict[str, Any]] = None):
        """
        Display performance metrics
        
        Args:
            query_history: List of query history with timing info
        """
        if not query_history:
            return
        
        # Calculate performance metrics
        total_queries = len(query_history)
        avg_response_time = sum(
            q.get("response_time", 0) for q in query_history
        ) / total_queries if total_queries > 0 else 0
        
        # Display performance metrics
        st.markdown("### 📈 Performance Metrics")
        
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_queries}</div>
            <div class="metric-label">Total Queries</div>
            <div class="metric-sublabel">Session</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_response_time:.2f}s</div>
            <div class="metric-label">Avg Response Time</div>
            <div class="metric-sublabel">Per query</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def display_status_indicator(self, status: str, label: str):
        """
        Display status indicator
        
        Args:
            status: Status type ('ready', 'processing', 'error')
            label: Status label
        """
        status_class = f"status-{status}"
        st.markdown(f"""
        <div class="system-info">
            <div class="status-indicator {status_class}"></div>
            <strong>{label}</strong>
        </div>
        """, unsafe_allow_html=True)
