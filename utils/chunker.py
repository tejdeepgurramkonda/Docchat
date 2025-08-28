"""
Text Chunker Module
Handles text splitting and chunking for document processing
"""

import logging
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    """
    Handles text chunking for document processing
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, encoding_name: str = "cl100k_base"):
        """
        Initialize the TextChunker
        
        Args:
            chunk_size (int): Maximum size of each chunk in tokens
            chunk_overlap (int): Number of tokens to overlap between chunks
            encoding_name (str): Encoding to use for token counting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding_name = encoding_name
        
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Could not load encoding {encoding_name}: {str(e)}")
            self.encoding = None
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self._token_len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _token_len(self, text: str) -> int:
        """
        Calculate the number of tokens in a text
        
        Args:
            text (str): Input text
            
        Returns:
            int: Number of tokens
        """
        if self.encoding is None:
            # Fallback to character count divided by 4 (rough estimate)
            return len(text) // 4
        
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {str(e)}")
            return len(text) // 4
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text (str): Input text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Filter out very small chunks
            min_chunk_size = 50  # Minimum 50 characters
            filtered_chunks = [chunk for chunk in chunks if len(chunk.strip()) >= min_chunk_size]
            
            logger.info(f"Successfully created {len(filtered_chunks)} chunks from {len(text)} characters")
            
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and preprocess text before chunking
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove or replace problematic characters
        text = text.replace('\x00', '')  # Remove null bytes
        text = text.replace('\r\n', '\n')  # Normalize line endings
        text = text.replace('\r', '\n')
        
        # Remove excessive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text
    
    def get_chunk_stats(self, chunks: List[str]) -> dict:
        """
        Get statistics about the chunks
        
        Args:
            chunks (List[str]): List of text chunks
            
        Returns:
            dict: Statistics about the chunks
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_tokens': 0,
                'total_characters': 0,
                'avg_tokens_per_chunk': 0,
                'avg_characters_per_chunk': 0,
                'max_tokens': 0,
                'min_tokens': 0
            }
        
        total_tokens = sum(self._token_len(chunk) for chunk in chunks)
        total_characters = sum(len(chunk) for chunk in chunks)
        token_counts = [self._token_len(chunk) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': total_tokens,
            'total_characters': total_characters,
            'avg_tokens_per_chunk': total_tokens / len(chunks),
            'avg_characters_per_chunk': total_characters / len(chunks),
            'max_tokens': max(token_counts),
            'min_tokens': min(token_counts)
        }
    
    def update_chunk_parameters(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Update chunking parameters
        
        Args:
            chunk_size (int): New chunk size
            chunk_overlap (int): New chunk overlap
        """
        if chunk_size is not None:
            self.chunk_size = chunk_size
        
        if chunk_overlap is not None:
            self.chunk_overlap = chunk_overlap
        
        # Reinitialize the text splitter with new parameters
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._token_len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(f"Updated chunk parameters: size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def chunk_with_metadata(self, text: str, source: str = None) -> List[dict]:
        """
        Chunk text and return with metadata
        
        Args:
            text (str): Input text to chunk
            source (str): Source of the text (filename, URL, etc.)
            
        Returns:
            List[dict]: List of chunks with metadata
        """
        chunks = self.chunk_text(text)
        
        chunks_with_metadata = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'chunk_index': i,
                'chunk_size': len(chunk),
                'token_count': self._token_len(chunk),
                'source': source or 'unknown'
            }
            
            chunks_with_metadata.append({
                'content': chunk,
                'metadata': metadata
            })
        
        return chunks_with_metadata
