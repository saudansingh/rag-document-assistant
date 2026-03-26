"""
RAG Assistant - Main retrieval-augmented generation system
Combines vector search with Gemini AI for accurate document Q&A
"""

from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from ..config import Config
from ..vector_store.vector_store_manager import VectorStoreManager


class RAGAssistant:
    """Main RAG assistant for document question answering"""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """
        Initialize RAG assistant
        
        Args:
            vector_store_manager: Initialized vector store manager
        """
        self.vector_store_manager = vector_store_manager
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            google_api_key=Config.GOOGLE_API_KEY
        )
        
        # Create enhanced prompt for better accuracy (NO SOURCES IN ANSWER)
        self.prompt_template = PromptTemplate(
            template="""You are an expert document analysis assistant. Your task is to provide accurate, detailed answers based strictly on the provided document context.

CONTEXT FROM DOCUMENT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer ONLY using information from the provided context
2. If the answer is not in the context, say "I cannot find this information in the provided document"
3. Be precise and include relevant details from the document
4. If you mention specific data, quotes, or figures, be accurate
5. Provide comprehensive answers with proper context
6. IMPORTANT: Do NOT include source information, page numbers, or file names in your answer
7. Provide a clean, natural answer as if you're having a conversation

ANSWER:""",
            input_variables=["context", "question"]
        )
        
        # Create retriever with enhanced search
        self.retriever = vector_store_manager.get_retriever()
        
        # Create RAG chain
        self.chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def _format_docs(self, docs: List[Document]) -> str:
        """
        Format documents for context (clean, no source info)
        
        Args:
            docs: List of retrieved documents
            
        Returns:
            Formatted string with document content only
        """
        formatted_docs = []
        for doc in docs:
            # Only include the content, NO metadata
            formatted_doc = doc.page_content
            formatted_docs.append(formatted_doc)
        
        return "\n\n---\n\n".join(formatted_docs)
    
    def query(self, question: str) -> str:
        """
        Query the RAG system with a question
        
        Args:
            question: User question
            
        Returns:
            Generated answer based on document context
        """
        try:
            if not question or not question.strip():
                return "Please provide a valid question."
            
            # Debug: Check what documents are retrieved
            retrieved_docs = self.vector_store_manager.similarity_search(question, k=5)
            
            if not retrieved_docs:
                return "No relevant documents found. Please try rephrasing your question or upload more documents."
            
            # Debug: Print retrieved content (for troubleshooting)
            print(f"Retrieved {len(retrieved_docs)} documents for question: {question}")
            for i, doc in enumerate(retrieved_docs):
                print(f"Doc {i+1}: {doc.page_content[:100]}...")
            
            # Get response from RAG chain
            response = self.chain.invoke(question.strip())
            
            return response
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def query_with_sources(self, question: str) -> Dict[str, Any]:
        """
        Query with detailed source information
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and source information
        """
        try:
            # Get retrieved documents
            retrieved_docs = self.vector_store_manager.similarity_search_with_score(
                question, k=Config.RETRIEVAL_TOP_K
            )
            
            # Get answer
            answer = self.query(question)
            
            # Extract source information
            sources = []
            for doc, score in retrieved_docs:
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score),
                    "source": doc.metadata.get('source', 'Unknown'),
                    "page": doc.metadata.get('page_number', 'N/A'),
                    "file": doc.metadata.get('original_file', 'Unknown')
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "question": question,
                "retrieved_docs_count": len(retrieved_docs)
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "question": question,
                "retrieved_docs_count": 0
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the RAG system
        
        Returns:
            Dictionary with system information
        """
        return {
            "llm_model": Config.LLM_MODEL,
            "llm_temperature": Config.LLM_TEMPERATURE,
            "retrieval_config": {
                "top_k": Config.RETRIEVAL_TOP_K,
                "similarity_threshold": Config.SIMILARITY_THRESHOLD
            },
            "vector_store_info": self.vector_store_manager.get_vector_store_info(),
            "prompt_template_length": len(self.prompt_template.template)
        }
