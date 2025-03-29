# FAQ Database Implementation Specification

## 1. Overview

The FAQ Database is one of the four vector databases in the StudyIndexer system. It stores static institutional information such as grading policies, exam formats, and other frequently asked questions. This document provides detailed specifications for implementing the FAQ database.

## 2. Data Model

### 2.1 FAQ Item Schema

```python
class FAQItem(BaseModel):
    """FAQ item model with validation"""
    question: str = Field(..., min_length=5, max_length=500, description="The FAQ question")
    answer: str = Field(..., min_length=10, max_length=5000, description="The FAQ answer")
    category: str = Field(..., min_length=2, max_length=100, description="Category of the FAQ")
    tags: List[str] = Field(default=[], description="Tags for filtering and categorization")
    source: Optional[str] = Field(None, description="Source of the information")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created this FAQ")
    is_published: bool = Field(True, description="Whether this FAQ is publicly visible")
    priority: int = Field(default=0, ge=0, le=100, description="Priority/importance (0-100)")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format"""
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag length must not exceed 50 characters")
                if not tag.replace('-', '').replace('_', '').isalnum():
                    raise ValueError("Tags must contain only alphanumeric characters, hyphens, and underscores")
        return v
```

### 2.2 FAQ Search Query

```python
class FAQSearchQuery(BaseModel):
    """Query model for FAQ search"""
    query: str = Field(..., min_length=3, max_length=500, description="Search query text")
    tags: Optional[List[str]] = Field(None, description="Filter by specific tags")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    min_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum similarity score")
```

### 2.3 FAQ Search Result

```python
class FAQSearchResult(BaseModel):
    """Search result model for FAQ items"""
    question: str
    answer: str
    category: str
    tags: List[str]
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    source: Optional[str] = None
    last_updated: datetime
```

### 2.4 FAQ Response Models

```python
class FAQResponse(BaseModel):
    """Standard response for FAQ operations"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
class FAQSearchResponse(BaseModel):
    """Response model for FAQ search operations"""
    success: bool
    results: List[FAQSearchResult]
    query: str
    total_results: int
    query_time_ms: float
```

## 3. API Endpoints

### 3.1 Search FAQs

```
POST /api/v1/faq/search
```

**Request Body:**
```json
{
  "query": "Can I carry a calculator to the exam?",
  "tags": ["exam", "policy"],
  "category": "Exams",
  "limit": 5,
  "min_score": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "question": "What items are allowed in the examination hall?",
      "answer": "Calculators are allowed in exams unless stated otherwise. Other permitted items include...",
      "category": "Exams",
      "tags": ["exam", "policy", "rules"],
      "score": 0.89,
      "source": "Student Handbook 2024",
      "last_updated": "2024-02-15T14:30:00Z"
    },
    ...
  ],
  "query": "Can I carry a calculator to the exam?",
  "total_results": 3,
  "query_time_ms": 45.8
}
```

### 3.2 Add FAQ

```
POST /api/v1/faq/add
```

**Request Body:**
```json
{
  "question": "Are calculators allowed in exams?",
  "answer": "Calculators are allowed in exams unless stated otherwise in the course syllabus. Scientific calculators are permitted, but models with wireless connectivity or programming capabilities may be restricted.",
  "category": "Exams",
  "tags": ["exam", "policy", "calculators"],
  "source": "Student Handbook 2024",
  "is_published": true,
  "priority": 80
}
```

**Response:**
```json
{
  "success": true,
  "message": "FAQ added successfully",
  "data": {
    "id": "faq_12345",
    "question": "Are calculators allowed in exams?",
    "category": "Exams"
  }
}
```

### 3.3 Update FAQ

```
PUT /api/v1/faq/{faq_id}
```

**Request Body:**
```json
{
  "answer": "Updated information: Calculators are allowed in most exams. Check your course syllabus for specific restrictions.",
  "tags": ["exam", "policy", "calculators", "updated"],
  "is_published": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "FAQ updated successfully",
  "data": {
    "id": "faq_12345",
    "question": "Are calculators allowed in exams?",
    "last_updated": "2024-03-18T10:15:00Z"
  }
}
```

### 3.4 Delete FAQ

```
DELETE /api/v1/faq/{faq_id}
```

**Response:**
```json
{
  "success": true,
  "message": "FAQ deleted successfully"
}
```

### 3.5 List FAQs by Category

```
GET /api/v1/faq/categories/{category_name}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "question": "Are calculators allowed in exams?",
      "answer": "Calculators are allowed in exams unless stated otherwise...",
      "category": "Exams",
      "tags": ["exam", "policy", "calculators"],
      "source": "Student Handbook 2024",
      "last_updated": "2024-03-18T10:15:00Z"
    },
    ...
  ],
  "category": "Exams",
  "total_results": 15
}
```

## 4. Service Layer

### 4.1 FAQ Service Interface

```python
class FAQService:
    """Service for managing FAQ items"""
    
    def __init__(self, chroma_service: ChromaService, embedding_service: EmbeddingService):
        self.chroma = chroma_service
        self.embedder = embedding_service
        self.collection_name = "faq_collection"
        
    async def initialize(self):
        """Initialize the FAQ collection"""
        metadata = {
            "description": "FAQ collection for institutional information",
            "type": "faq",
            "schema_version": "1.0"
        }
        self.collection = await self.chroma.get_or_create_collection(
            name=self.collection_name,
            metadata=metadata
        )
        
    async def add_faq(self, faq_item: FAQItem, user_id: str) -> str:
        """Add a new FAQ item to the collection"""
        # Generate ID
        faq_id = f"faq_{uuid.uuid4().hex}"
        
        # Add created_by if not provided
        if not faq_item.created_by:
            faq_item.created_by = user_id
            
        # Convert to dict for storage
        faq_dict = faq_item.model_dump()
        
        # Generate combined text for embedding
        combined_text = f"QUESTION: {faq_item.question}\nANSWER: {faq_item.answer}"
        
        # Generate embedding
        embedding = self.embedder.generate_embedding(combined_text)
        
        # Add metadata
        metadata = {
            "id": faq_id,
            "question": faq_item.question,
            "category": faq_item.category,
            "tags": ",".join(faq_item.tags),
            "is_published": faq_item.is_published,
            "created_by": faq_item.created_by,
            "priority": faq_item.priority,
            "type": "faq"
        }
        
        # Store in collection
        await self.chroma.add_documents(
            collection_name=self.collection_name,
            documents=[combined_text],
            metadatas=[metadata],
            ids=[faq_id],
            embeddings=[embedding]
        )
        
        return faq_id
        
    async def search_faqs(self, search_query: FAQSearchQuery) -> Tuple[int, List[FAQSearchResult]]:
        """Search for FAQs based on the query"""
        # Prepare filters
        filters = {}
        
        if search_query.tags:
            tag_conditions = []
            for tag in search_query.tags:
                tag_conditions.append({"tags": {"$contains": tag}})
            if tag_conditions:
                filters["$or"] = tag_conditions
                
        if search_query.category:
            if "$or" in filters:
                filters = {"$and": [filters, {"category": search_query.category}]}
            else:
                filters["category"] = search_query.category
                
        # Always filter by published status for non-admin users
        # This would typically come from a parameter, here we're setting a default
        include_unpublished = False
        if not include_unpublished:
            if "$and" in filters:
                filters["$and"].append({"is_published": True})
            elif filters:
                filters = {"$and": [filters, {"is_published": True}]}
            else:
                filters["is_published"] = True
        
        # Generate embedding for query
        query_embedding = self.embedder.generate_embedding(search_query.query)
        
        # Search collection
        results = await self.chroma.search(
            collection_name=self.collection_name,
            query=search_query.query,
            query_embedding=query_embedding,
            n_results=search_query.limit,
            where=filters,
            include_metadata=True,
            include_values=True
        )
        
        # Process results
        faq_results = []
        for i, (doc, metadata, score) in enumerate(zip(results.documents, results.metadatas, results.distances)):
            # Convert distance to similarity score (1 - distance)
            similarity = 1.0 - min(score, 1.0)
            
            # Skip results below minimum score
            if similarity < search_query.min_score:
                continue
                
            # Extract question and answer from document
            parts = doc.split("\nANSWER: ", 1)
            question = parts[0].replace("QUESTION: ", "") if len(parts) > 0 else ""
            answer = parts[1] if len(parts) > 1 else doc
                
            # Get tags as list
            tags = metadata.get("tags", "").split(",") if metadata.get("tags") else []
            
            # Create result object
            faq_result = FAQSearchResult(
                question=question,
                answer=answer,
                category=metadata.get("category", ""),
                tags=tags,
                score=similarity,
                source=metadata.get("source"),
                last_updated=datetime.fromisoformat(metadata.get("last_updated", datetime.utcnow().isoformat()))
            )
            faq_results.append(faq_result)
            
        return len(faq_results), faq_results
        
    async def update_faq(self, faq_id: str, faq_update: Dict[str, Any]) -> bool:
        """Update an existing FAQ item"""
        # Get current FAQ
        results = await self.chroma.get(
            collection_name=self.collection_name,
            ids=[faq_id],
            include_metadata=True,
            include_values=True
        )
        
        if not results.documents or len(results.documents) == 0:
            return False
            
        # Get current document and metadata
        current_doc = results.documents[0]
        current_metadata = results.metadatas[0]
        
        # Parse current document
        parts = current_doc.split("\nANSWER: ", 1)
        question = parts[0].replace("QUESTION: ", "") if len(parts) > 0 else ""
        answer = parts[1] if len(parts) > 1 else current_doc
        
        # Update fields
        new_question = faq_update.get("question", question)
        new_answer = faq_update.get("answer", answer)
        
        # Create new document
        new_doc = f"QUESTION: {new_question}\nANSWER: {new_answer}"
        
        # Update metadata
        new_metadata = dict(current_metadata)
        for key, value in faq_update.items():
            if key == "tags" and isinstance(value, list):
                new_metadata[key] = ",".join(value)
            elif key != "question" and key != "answer":
                new_metadata[key] = value
                
        # Update timestamp
        new_metadata["last_updated"] = datetime.utcnow().isoformat()
        
        # Generate new embedding
        new_embedding = self.embedder.generate_embedding(new_doc)
        
        # Update in collection
        await self.chroma.update(
            collection_name=self.collection_name,
            ids=[faq_id],
            documents=[new_doc],
            metadatas=[new_metadata],
            embeddings=[new_embedding]
        )
        
        return True
        
    async def delete_faq(self, faq_id: str) -> bool:
        """Delete an FAQ item"""
        try:
            await self.chroma.delete(
                collection_name=self.collection_name,
                ids=[faq_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting FAQ {faq_id}: {str(e)}")
            return False
            
    async def get_categories(self) -> List[str]:
        """Get all FAQ categories"""
        results = await self.chroma.get_metadata_keys(
            collection_name=self.collection_name,
            key="category"
        )
        return sorted(list(set(results)))
```

## 5. Implementation Notes

### 5.1 Embedding Strategy

For FAQ items, we combine the question and answer text to create a single document for embedding, with clear markers for each part. This allows us to:

1. Find FAQs based on similarity to either the question or answer
2. Maintain the semantic relationship between questions and answers
3. Easily parse the combined text back into separate fields for display

### 5.2 Storage Considerations

FAQ data is generally static and smaller in volume compared to course content, so the FAQ collection will be very efficient. No chunking is necessary since FAQs are typically brief and self-contained.

### 5.3 Security

Only authorized users (admins, teachers) should be able to add, update, or delete FAQs. All users can search and view published FAQs.

### 5.4 Testing Strategy

Key test cases should include:
- Adding FAQs with various tags and categories
- Searching with different queries and filters
- Updating FAQs and verifying changes
- Testing the exclusion of unpublished FAQs
- Performance testing with a large number of FAQs

## 6. Integration with Other Components

### 6.1 Perceptron Chat Assistant

The Perceptron chat assistant will use the FAQ database as a primary source for answering institutional questions. The integration should:

1. Prioritize FAQ database searches for basic institutional questions
2. Use high similarity threshold (0.7+) for direct answers
3. For lower similarity matches, present the information as a suggestion

### 6.2 Course Content Database

When a student asks about course-specific policies, the system should:

1. First check the FAQ database for institution-wide policies
2. Then check the specific course's content for any course-specific overrides

This requires coordination between the FAQ service and the Course Content service.

## 7. Future Enhancements

1. **FAQ Analytics**: Track which FAQs are frequently accessed to improve content
2. **Auto-FAQ Generation**: Analyze support tickets and forum questions to identify new FAQs
3. **Versioning**: Keep track of FAQ changes over time for different academic years
4. **Personalized FAQ Ranking**: Boost FAQ relevance based on user's course enrollments 