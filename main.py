"""
Main application entry point for Advanced RAG Document Assistant
Modular architecture with clear separation of concerns
"""

import streamlit as st
import os
import sys
from typing import List, Dict, Any

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.document_processors import DocumentProcessor
from src.vector_store import VectorStoreManager, EmbeddingManager
from src.rag_pipeline import RAGAssistant
from src.ui import ChatInterface, DocumentUploader, MetricsDisplay


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'vector_store_manager' not in st.session_state:
        st.session_state.vector_store_manager = None
    if 'rag_assistant' not in st.session_state:
        st.session_state.rag_assistant = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'document_info' not in st.session_state:
        st.session_state.document_info = {}
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'processed' not in st.session_state:
        st.session_state.processed = False


def apply_app_styling():
    """Apply application-wide styling"""
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.APP_ICON,
        layout=Config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Main header styling
    st.markdown(f"""
    <style>
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
        }}
        .sidebar-content {{
            padding: 1rem;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>RAG Document Assistant</h1>
        <p>Upload documents and get accurate answers</p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display clean sidebar with only upload button"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # Simple upload button only
        uploader = DocumentUploader()
        uploaded_files = uploader.display_upload_interface()
        
        if uploader.display_processing_button(uploaded_files):
            process_documents(uploaded_files, uploader)
        
        # Simple file info
        if st.session_state.document_info:
            st.markdown("### Documents")
            for doc_name, info in st.session_state.document_info.items():
                if info.get("status") == "success":
                    st.markdown(f"✅ {doc_name}: {info.get('chunks', 0)} chunks")
        
        # Clear button
        if st.button("Clear", use_container_width=True):
            clear_session_state()
        
        st.markdown('</div>', unsafe_allow_html=True)


def process_documents(uploaded_files: List, uploader: DocumentUploader):
    """Process uploaded documents and create RAG system"""
    try:
        # Process documents
        all_documents, document_info, processing_errors = uploader.process_documents(uploaded_files)
        
        if not all_documents:
            st.error("No documents were successfully processed.")
            return
        
        # Create vector store
        vector_store_manager = VectorStoreManager()
        vector_store = vector_store_manager.create_vector_store(all_documents)
        
        # Create RAG assistant
        rag_assistant = RAGAssistant(vector_store_manager)
        
        # Update session state
        st.session_state.vector_store_manager = vector_store_manager
        st.session_state.rag_assistant = rag_assistant
        st.session_state.document_info = document_info
        st.session_state.processed = True
        st.session_state.chat_history = []  # Clear chat history for new documents
        
        # Display results
        uploader.display_processing_results(document_info, processing_errors)
        
        # Display metrics
        metrics = MetricsDisplay()
        metrics.apply_custom_css()
        metrics.display_processing_metrics(document_info)
        
        st.success("🎉 Documents processed successfully! You can now ask questions.")
        
    except Exception as e:
        st.error(f"❌ Error processing documents: {str(e)}")
        st.session_state.processed = False


def display_main_interface():
    """Display clean chat interface"""
    chat_interface = ChatInterface()
    chat_interface.apply_custom_css()
    
    if not st.session_state.processed or not st.session_state.rag_assistant:
        # Simple welcome message
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>Upload Documents to Get Started</h2>
            <p>Upload PDF, Word, or Text files to ask questions</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Simple chat interface
    st.markdown("### Ask Questions")
    
    # Display chat history
    chat_interface.display_chat_history(st.session_state.chat_history)
    
    # Get user question
    user_question = chat_interface.get_user_question()
    
    if user_question:
        # Add user message
        st.session_state.chat_history = chat_interface.add_message_to_history(
            st.session_state.chat_history, user_question, is_user=True
        )
        
        # Show typing indicator
        chat_interface.display_chat_message(
            "Thinking...", is_user=False
        )
        
        # Process query
        try:
            import time
            start_time = time.time()
            
            response = st.session_state.rag_assistant.query(user_question)
            response_time = time.time() - start_time
            
            # Remove typing indicator
            st.session_state.chat_history.pop()
            
            # Add assistant response
            st.session_state.chat_history = chat_interface.add_message_to_history(
                st.session_state.chat_history, 
                response, 
                is_user=False
            )
            
            # Track query
            st.session_state.query_history.append({
                "question": user_question,
                "response": response,
                "response_time": response_time
            })
            
        except Exception as e:
            # Remove typing indicator and add error message
            st.session_state.chat_history.pop()
            st.session_state.chat_history = chat_interface.add_message_to_history(
                st.session_state.chat_history,
                f"Error: {str(e)}",
                is_user=False
            )
        
        st.rerun()


def clear_session_state():
    """Clear all session state"""
    st.session_state.vector_store_manager = None
    st.session_state.rag_assistant = None
    st.session_state.chat_history = []
    st.session_state.document_info = {}
    st.session_state.query_history = []
    st.session_state.processed = False
    st.rerun()


def main():
    """Main application entry point"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize session state
        initialize_session_state()
        
        # Apply styling
        apply_app_styling()
        
        # Display sidebar
        display_sidebar()
        
        # Display main interface
        display_main_interface()
        
    except ValueError as e:
        if "GOOGLE_API_KEY" in str(e):
            st.error("🚨 Please set GOOGLE_API_KEY in your .env file")
            st.info("Get your API key from: https://makersuite.google.com/app/apikey")
            st.info("1. Copy .env.example to .env")
            st.info("2. Add your GOOGLE_API_KEY")
            st.info("3. Restart the application")
        else:
            st.error(f"Configuration error: {str(e)}")
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
