# Embedding Service Implementation Specification

## 1. Overview

The Embedding Service is a core component of the StudyIndexer system, providing vector embeddings for all four vector databases. This service uses sentence-transformers to convert text into high-dimensional vector representations that enable semantic search capabilities. This document provides detailed specifications for implementing the shared embedding service.

## 2. Requirements

The Embedding Service must:

1. Generate consistent, high-quality text embeddings for all text content
2. Support batch processing for efficiency
3. Provide both synchronous and asynchronous interfaces
4. Handle errors gracefully
5. Maintain compatibility with ChromaDB
6. Support document chunking and preprocessing
7. Optimize for performance and resource usage

## 3. Technical Specifications

### 3.1 Embedding Model

```python
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List, Union, Optional

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
            print(f"Embedding model {self.model_name} loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
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
        import concurrent.futures
        from asyncio import get_event_loop
        
        loop = get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.generate_embedding, text
            )
    
    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings asynchronously (batch processing)"""
        import concurrent.futures
        from asyncio import get_event_loop
        
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
        import re
        processed = re.sub(r'\s+', ' ', processed)
        
        return processed
    
    def get_dimensions(self) -> int:
        """Get the number of dimensions in the embedding"""
        return self.embedding_dim
    
    def is_initialized(self) -> bool:
        """Check if the model is initialized"""
        return self._initialized and self.model is not None
```

### 3.2 Document Chunking Utility

```python
from typing import List, Dict, Any, Optional
import re

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
```

## 4. Integration with Vector Databases

### 4.1 ChromaDB Integration

```python
class ChromaEmbeddingFunction:
    """Embedding function for ChromaDB"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for ChromaDB"""
        return self.embedding_service.generate_embeddings(texts)
```

### 4.2 Usage in Services

Each vector database service will use the EmbeddingService as follows:

```python
from app.services.embeddings import EmbeddingService

class FaqService:
    def __init__(self):
        self.embedder = EmbeddingService()
        # Initialize other dependencies
        
    async def add_faq(self, faq_item):
        # Generate embedding for FAQ
        combined_text = f"QUESTION: {faq_item.question}\nANSWER: {faq_item.answer}"
        embedding = await self.embedder.generate_embedding_async(combined_text)
        
        # Add to ChromaDB
        # ...
```

## 5. Performance Considerations

### 5.1 Batch Processing

For optimal performance, the embedding service batches requests whenever possible:

```python
# Instead of:
for text in texts:
    embedding = embedder.generate_embedding(text)  # Inefficient
    
# Use:
embeddings = embedder.generate_embeddings(texts)  # Efficient batch processing
```

### 5.2 Memory Optimization

```python
# Limit batch size to avoid memory issues
MAX_BATCH_SIZE = 32

def process_large_dataset(texts):
    all_embeddings = []
    for i in range(0, len(texts), MAX_BATCH_SIZE):
        batch = texts[i:i + MAX_BATCH_SIZE]
        batch_embeddings = embedder.generate_embeddings(batch)
        all_embeddings.extend(batch_embeddings)
    return all_embeddings
```

### 5.3 GPU Acceleration

The embedding service can use GPU acceleration if available:

```python
import torch

# Check if CUDA is available and configure accordingly
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

embedder = EmbeddingService(device=device)
```

## 6. Error Handling and Resilience

### 6.1 Automatic Fallback

```python
def generate_embedding_with_fallback(text):
    try:
        return embedder.generate_embedding(text)
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return a zero vector as fallback
        return [0.0] * embedder.get_dimensions()
```

### 6.2 Model Reloading

```python
def reload_model_if_needed():
    if not embedder.is_initialized():
        try:
            embedder = EmbeddingService()
            print("Model reloaded successfully")
        except Exception as e:
            print(f"Failed to reload model: {str(e)}")
```

## 7. Testing Strategy

### 7.1 Unit Tests

```python
def test_embedding_consistency():
    """Test that the same text produces consistent embeddings"""
    text = "This is a test sentence for embedding"
    
    embedding1 = embedder.generate_embedding(text)
    embedding2 = embedder.generate_embedding(text)
    
    # Calculate cosine similarity
    similarity = calculate_cosine_similarity(embedding1, embedding2)
    
    # Should be almost identical
    assert similarity > 0.9999

def test_semantic_similarity():
    """Test that semantically similar texts have similar embeddings"""
    text1 = "How do I reset my password?"
    text2 = "I forgot my password, how can I get a new one?"
    text3 = "What are the library hours on weekends?"
    
    emb1 = embedder.generate_embedding(text1)
    emb2 = embedder.generate_embedding(text2)
    emb3 = embedder.generate_embedding(text3)
    
    # Similar questions should have high similarity
    sim12 = calculate_cosine_similarity(emb1, emb2)
    # Different questions should have lower similarity
    sim13 = calculate_cosine_similarity(emb1, emb3)
    
    assert sim12 > 0.8  # High similarity for related questions
    assert sim13 < 0.5  # Lower similarity for unrelated questions
```

### 7.2 Performance Tests

```python
def test_batch_performance():
    """Test batch processing performance"""
    import time
    
    # Generate 100 test texts
    texts = [f"This is test text {i}" for i in range(100)]
    
    # Measure time for individual processing
    start_time = time.time()
    individual_embeddings = []
    for text in texts:
        individual_embeddings.append(embedder.generate_embedding(text))
    individual_time = time.time() - start_time
    
    # Measure time for batch processing
    start_time = time.time()
    batch_embeddings = embedder.generate_embeddings(texts)
    batch_time = time.time() - start_time
    
    # Batch should be significantly faster
    print(f"Individual time: {individual_time:.2f}s, Batch time: {batch_time:.2f}s")
    assert batch_time < individual_time
```

## 8. Future Enhancements

1. **Model Switching**: Add support for switching between multiple embedding models
2. **Embedding Cache**: Implement caching to avoid recomputing embeddings for the same text
3. **Quantization**: Support model quantization for faster inference
4. **Custom Models**: Allow fine-tuning on domain-specific data
5. **Distributed Processing**: Support distributed processing for very large datasets

## 9. Conclusion

The Embedding Service provides a robust, high-performance foundation for semantic search across all vector databases in the StudyIndexer system. By centralizing this functionality, we ensure consistent behavior, efficient resource usage, and simplified maintenance. 