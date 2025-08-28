"""
Document Embedder Module
Handles text embedding and vector store creation
"""

import logging
import os
import pickle
from turtle import st
from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """
    Handles document embedding and vector store operations
    """
    
    def __init__(self, model_name: str = "models/embedding-001"):
        """
        Initialize the DocumentEmbedder
        
        Args:
            model_name (str): Name of the embedding model to use
        """
        self.model_name = model_name
        self.embeddings = None
        self.vector_store = None
        
        # Initialize Google Gemini embeddings
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
            logger.info(f"Initialized Google Gemini embeddings with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Google Gemini embeddings: {str(e)}")
            st.error("Failed to initialize embeddings. Please check your Google API key.")
    
    def create_vector_store(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> Optional[FAISS]:
        """
        Create a vector store from text chunks
        
        Args:
            texts (List[str]): List of text chunks
            metadatas (Optional[List[dict]]): Optional metadata for each chunk
            
        Returns:
            Optional[FAISS]: FAISS vector store or None if creation failed
        """
        if not texts:
            logger.warning("No texts provided for vector store creation")
            return None
        
        if self.embeddings is None:
            logger.error("Embeddings not initialized")
            return None
        
        try:
            # Create documents
            documents = []
            for i, text in enumerate(texts):
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {'chunk_id': i}
                documents.append(Document(page_content=text, metadata=metadata))
            
            # Create vector store
            logger.info(f"Creating vector store with {len(documents)} documents...")
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
            logger.info("Vector store created successfully")
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            st.error(f"Failed to create vector store: {str(e)}")
            return None
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> bool:
        """
        Add new texts to existing vector store
        
        Args:
            texts (List[str]): List of text chunks to add
            metadatas (Optional[List[dict]]): Optional metadata for each chunk
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return False
        
        try:
            self.vector_store.add_texts(texts, metadatas)
            logger.info(f"Added {len(texts)} texts to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding texts to vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search on the vector store
        
        Args:
            query (str): Query text
            k (int): Number of similar documents to return
            
        Returns:
            List[Document]: List of similar documents
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(docs)} similar documents for query")
            return docs
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query (str): Query text
            k (int): Number of similar documents to return
            
        Returns:
            List[tuple]: List of (document, score) tuples
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return []
        
        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(docs_with_scores)} similar documents with scores")
            return docs_with_scores
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {str(e)}")
            return []
    
    def save_vector_store(self, file_path: str = "vector_store/faiss_index.pkl") -> bool:
        """
        Save the vector store to disk
        
        Args:
            file_path (str): Path to save the vector store
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the vector store
            with open(file_path, 'wb') as f:
                pickle.dump(self.vector_store, f)
            
            logger.info(f"Vector store saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            return False
    
    def load_vector_store(self, file_path: str = "vector_store/faiss_index.pkl") -> bool:
        """
        Load a vector store from disk
        
        Args:
            file_path (str): Path to load the vector store from
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logger.warning(f"Vector store file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                self.vector_store = pickle.load(f)
            
            logger.info(f"Vector store loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def get_vector_store_info(self) -> dict:
        """
        Get information about the current vector store
        
        Returns:
            dict: Information about the vector store
        """
        if not self.vector_store:
            return {
                'initialized': False,
                'document_count': 0,
                'embedding_model': self.model_name
            }
        
        try:
            # Get number of documents
            doc_count = len(self.vector_store.index_to_docstore_id)
            
            return {
                'initialized': True,
                'document_count': doc_count,
                'embedding_model': self.model_name,
                'vector_dimension': self.vector_store.index.d if hasattr(self.vector_store.index, 'd') else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error getting vector store info: {str(e)}")
            return {
                'initialized': True,
                'document_count': 'unknown',
                'embedding_model': self.model_name,
                'error': str(e)
            }
    
    def clear_vector_store(self):
        """
        Clear the current vector store
        """
        self.vector_store = None
        logger.info("Vector store cleared")
    
    def get_relevant_context(self, query: str, max_tokens: int = 4000) -> str:
        """
        Get relevant context for a query, respecting token limits
        
        Args:
            query (str): User query
            max_tokens (int): Maximum tokens to include in context
            
        Returns:
            str: Relevant context string
        """
        if not self.vector_store:
            return ""
        
        try:
            # Get similar documents with scores
            docs_with_scores = self.similarity_search_with_score(query, k=10)
            
            # Filter documents by relevance score (lower is better for FAISS)
            relevant_docs = [doc for doc, score in docs_with_scores if score < 0.8]
            
            # Build context string
            context_parts = []
            current_tokens = 0
            
            for doc in relevant_docs:
                # Rough token estimation (1 token ≈ 4 characters)
                doc_tokens = len(doc.page_content) // 4
                
                if current_tokens + doc_tokens > max_tokens:
                    break
                
                context_parts.append(doc.page_content)
                current_tokens += doc_tokens
            
            context = "\n\n".join(context_parts)
            logger.info(f"Retrieved context with approximately {current_tokens} tokens")
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return ""
