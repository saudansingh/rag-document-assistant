"""
Chat interface for RAG Assistant
Modern ChatGPT-style chat interface with message history
"""

import streamlit as st
from typing import List, Dict, Any
from ..config import Config


class ChatInterface:
    """Modern chat interface for RAG Assistant"""
    
    def __init__(self):
        """Initialize chat interface"""
        self.custom_css = self._get_custom_css()
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for chat interface"""
        return """
        <style>
            .chat-container {
                max-width: 800px;
                margin: 0 auto;
                padding: 1rem;
            }
            .message {
                padding: 1rem;
                border-radius: 18px;
                margin: 0.5rem 0;
                max-width: 70%;
                display: flex;
                align-items: flex-start;
                animation: fadeIn 0.3s ease-in;
            }
            .user-message {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .assistant-message {
                background: #f1f3f4;
                color: #202124;
                margin-right: auto;
            }
            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                margin: 0 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                flex-shrink: 0;
            }
            .user-avatar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .assistant-avatar {
                background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
            }
            .message-content {
                flex: 1;
            }
            .message-time {
                font-size: 0.8rem;
                opacity: 0.7;
                margin-top: 0.5rem;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .typing-indicator {
                display: inline-block;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
        """
    
    def apply_custom_css(self):
        """Apply custom CSS to the app"""
        st.markdown(self.custom_css, unsafe_allow_html=True)
    
    def display_chat_message(self, message: str, is_user: bool = False, timestamp: str = None):
        """
        Display a chat message
        
        Args:
            message: Message content
            is_user: Whether this is a user message
            timestamp: Optional timestamp
        """
        avatar = "U" if is_user else "AI"
        avatar_class = "user-avatar" if is_user else "assistant-avatar"
        message_class = "user-message" if is_user else "assistant-message"
        
        time_display = f'<div class="message-time">{timestamp}</div>' if timestamp else ''
        
        st.markdown(f"""
        <div class="message {message_class}">
            <div class="message-avatar {avatar_class}">{avatar}</div>
            <div class="message-content">
                {message}
                {time_display}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_chat_history(self, chat_history: List[Dict[str, Any]]):
        """
        Display entire chat history
        
        Args:
            chat_history: List of chat messages
        """
        chat_container = st.container()
        
        with chat_container:
            for message in chat_history:
                self.display_chat_message(
                    message["content"],
                    message.get("is_user", False),
                    message.get("timestamp")
                )
    
    def get_user_question(self) -> str:
        """
        Get user question from simple input
        
        Returns:
            User question string
        """
        with st.form(key="chat_form", clear_on_submit=True):
            user_question = st.text_input(
                "Ask a question...",
                placeholder="Type your question here...",
                key="question_input",
                label_visibility="collapsed"
            )
            submit_button = st.form_submit_button("Send", type="primary")
        
        if submit_button and user_question:
            return user_question.strip()
        
        return ""
    
    def add_message_to_history(self, chat_history: List[Dict[str, Any]], 
                             content: str, is_user: bool = False) -> List[Dict[str, Any]]:
        """
        Add message to chat history (no sources for cleaner interface)
        
        Args:
            chat_history: Current chat history
            content: Message content
            is_user: Whether this is a user message
            
        Returns:
            Updated chat history
        """
        from datetime import datetime
        
        message = {
            "content": content,
            "is_user": is_user,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        chat_history.append(message)
        return chat_history
    
    def display_sources(self, sources: List[Dict[str, Any]]):
        """
        Display source information for a response
        
        Args:
            sources: List of source documents
        """
        if not sources:
            return
        
        with st.expander("📚 Sources", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"**Source {i}:**")
                st.markdown(f"- **File:** {source.get('file', 'Unknown')}")
                st.markdown(f"- **Page:** {source.get('page', 'N/A')}")
                st.markdown(f"- **Similarity:** {source.get('similarity_score', 0):.3f}")
                st.markdown(f"- **Content:** {source.get('content', '')}")
                st.markdown("---")
    
    def clear_chat_history(self) -> List[Dict[str, Any]]:
        """
        Clear chat history
        
        Returns:
            Empty chat history
        """
        return []
    
    def display_welcome_screen(self):
        """Display simple welcome screen when no documents are processed"""
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>Upload Documents to Get Started</h2>
            <p>Upload PDF, Word, or Text files to ask questions</p>
        </div>
        """, unsafe_allow_html=True)
