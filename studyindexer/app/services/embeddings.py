"""
Embedding service for generating vector embeddings of text
Based on the implementation specification in Embedding_Service_Implementation.md
"""
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List, Union, Optional, Dict, Any
import re
import concurrent.futures
from asyncio import get_event_loop
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one model is loaded"""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding model"""
        if getattr(self, '_initialized', False):
            return
            
        # Load configuration
        self.model_name = "all-MiniLM-L6-v2"  # From config
        self.device = "cpu"  # From config, could be "cuda" if available
        self.embedding_dim = 384  # all-MiniLM-L6-v2 has 384 dimensions
        
        # Initialize model
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self._initialized = True
            logger.info(f"Embedding model {self.model_name} loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            self.model = None
            self._initialized = False
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text string"""
        if not self._initialized or self.model is None:
            raise ValueError("Embedding model not initialized")
            
        # Preprocess text if needed
        processed_text = self._preprocess_text(text)
        
        # Generate embedding
        with torch.no_grad():
            embedding = self.model.encode(processed_text)
        
        # Convert to list of floats (compatible with ChromaDB)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch processing)"""
        if not self._initialized or self.model is None:
            raise ValueError("Embedding model not initialized")
            
        # Preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Generate embeddings in one batch for efficiency
        with torch.no_grad():
            embeddings = self.model.encode(processed_texts)
        
        # Convert to list of floats (compatible with ChromaDB)
        return embeddings.tolist()
    
    async def generate_embedding_async(self, text: str) -> List[float]:
        """Generate embedding asynchronously"""
        # For sentence-transformers, we'll use a thread pool to avoid blocking
        loop = get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.generate_embedding, text
            )
    
    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings asynchronously (batch processing)"""
        loop = get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.generate_embeddings, texts
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding"""
        if not text:
            return ""
            
        # Basic preprocessing
        processed = text.strip()
        
        # Remove excessive whitespace
        processed = re.sub(r'\s+', ' ', processed)
        
        return processed
    
    def get_dimensions(self) -> int:
        """Get the number of dimensions in the embedding"""
        return self.embedding_dim
    
    def is_initialized(self) -> bool:
        """Check if the model is initialized"""
        return self._initialized and self.model is not None


class TextChunker:
    """Utility for chunking documents into smaller pieces"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize with configuration"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        if not text:
            return []
            
        chunks = []
        
        # Split text into paragraphs first
        paragraphs = self._split_into_paragraphs(text)
        
        current_chunk = ""
        current_size = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if current_size + len(paragraph) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_data = {
                    "content": current_chunk.strip(),
                    "metadata": metadata.copy() if metadata else {}
                }
                chunks.append(chunk_data)
                
                # Start new chunk with overlap
                overlap_size = min(self.chunk_overlap, len(current_chunk))
                if overlap_size > 0:
                    current_chunk = current_chunk[-overlap_size:]
                    current_size = len(current_chunk)
                else:
                    current_chunk = ""
                    current_size = 0
            
            # Add paragraph to current chunk
            current_chunk += paragraph
            current_size += len(paragraph)
        
        # Add the last chunk if it's not empty
        if current_chunk.strip():
            chunk_data = {
                "content": current_chunk.strip(),
                "metadata": metadata.copy() if metadata else {}
            }
            chunks.append(chunk_data)
        
        # Add positional info to metadata
        for i, chunk in enumerate(chunks):
            chunk["metadata"]["chunk_index"] = i
            chunk["metadata"]["total_chunks"] = len(chunks)
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs while preserving structure"""
        # Split on double newlines (paragraph breaks)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Process paragraphs that are too long
        result = []
        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                result.append(paragraph + "\n\n")
            else:
                # Further split on single newlines
                subparagraphs = paragraph.split('\n')
                for subparagraph in subparagraphs:
                    if len(subparagraph) <= self.chunk_size:
                        result.append(subparagraph + "\n")
                    else:
                        # Split very long sentences
                        sentences = re.split(r'(?<=[.!?])\s+', subparagraph)
                        current = ""
                        for sentence in sentences:
                            if len(current) + len(sentence) <= self.chunk_size:
                                current += sentence + " "
                            else:
                                if current:
                                    result.append(current + "\n")
                                current = sentence + " "
                        if current:
                            result.append(current + "\n")
                result.append("\n")  # Add paragraph separator
        
        return result


class ChromaEmbeddingFunction:
    """Embedding function for ChromaDB"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for ChromaDB
        
        Note: The parameter must be named 'input' for newer ChromaDB versions
        """
        return self.embedding_service.generate_embeddings(input) 