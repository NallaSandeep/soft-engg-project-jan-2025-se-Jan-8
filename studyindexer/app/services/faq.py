"""
FAQ service for managing FAQ items
Based on the implementation specification in FAQ_Database_Implementation.md
"""
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import time
import aiofiles

from ..models.faq import FAQItem, FAQSearchQuery, FAQSearchResult, JSONLImportItem
from .chroma import ChromaService
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class FAQService:
    """Service for managing FAQ items"""
    
    def __init__(self, chroma_service: ChromaService = None, embedding_service: EmbeddingService = None):
        """Initialize with dependencies"""
        self.chroma = chroma_service or ChromaService()
        self.embedder = embedding_service or EmbeddingService()
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
        logger.info(f"FAQ collection initialized: {self.collection_name}")
        
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
        combined_text = f"TOPIC: {faq_item.topic}\nQUESTION: {faq_item.question}\nANSWER: {faq_item.answer}"
        
        # Generate embedding
        embedding = await self.embedder.generate_embedding_async(combined_text)
        
        # Add metadata - ensure all values are scalar types for ChromaDB compatibility
        metadata = {
            "id": faq_id,
            "topic": faq_item.topic,
            "question": faq_item.question,
            "tags": ",".join(faq_item.tags) if faq_item.tags else "",
            "is_published": faq_item.is_published,
            "created_by": faq_item.created_by,
            "priority": faq_item.priority,
            "source": faq_item.source,
            "last_updated": faq_item.last_updated.isoformat(),
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
        
        logger.info(f"Added FAQ item with ID: {faq_id}")
        return faq_id
        
    async def search_faqs(self, search_query: FAQSearchQuery) -> Tuple[int, List[FAQSearchResult], float]:
        """Search for FAQs based on the query"""
        start_time = time.time()
        
        # Prepare filters
        filter_conditions = []
        
        # Only add non-empty tags to filter
        if search_query.tags and any(tag.strip() for tag in search_query.tags):
            valid_tags = [tag for tag in search_query.tags if tag.strip()]
            # Use $in operator which is supported by ChromaDB
            if valid_tags:
                filter_conditions.append({"tags": {"$in": valid_tags}})
                
        # Only add non-empty topic
        if search_query.topic and search_query.topic.strip():
            filter_conditions.append({"topic": search_query.topic})
                
        # Only add non-empty source
        if search_query.source and search_query.source.strip():
            filter_conditions.append({"source": search_query.source})
                
        # Always filter by published status for non-admin users
        filter_conditions.append({"is_published": True})
        
        # Create the where clause
        where_clause = None
        if len(filter_conditions) == 1:
            where_clause = filter_conditions[0]
        else:
            where_clause = {"$and": filter_conditions}
        
        # Generate embedding for query (ensure we have valid search text)
        search_text = search_query.query if search_query.query else ""
        
        # If empty query and min_score is 0, just return all matching documents 
        # without semantic ranking
        if not search_text and search_query.min_score == 0:
            # Get collection info to determine how many documents to retrieve
            collection_info = await self.chroma.get_collection_info(self.collection_name)
            total_docs = collection_info["count"]
            limit = min(search_query.limit, total_docs)
            
            # Get all matching documents based on filters
            # This is a special case for empty queries with no score threshold
            results = await self.chroma.search(
                collection_name=self.collection_name,
                query="",
                n_results=limit,
                where=where_clause
            )
            
            # Process results without scoring
            faq_results = []
            for i, (doc, metadata, _) in enumerate(zip(results.documents, results.metadatas, results.distances)):
                # Extract question and answer from document
                try:
                    parts = doc.split("\n")
                    topic = parts[0].replace("TOPIC: ", "") if parts[0].startswith("TOPIC: ") else ""
                    question = parts[1].replace("QUESTION: ", "") if parts[1].startswith("QUESTION: ") else ""
                    answer = parts[2].replace("ANSWER: ", "") if len(parts) > 2 and parts[2].startswith("ANSWER: ") else ""
                except IndexError:
                    # Fallback for legacy data format
                    parts = doc.split("\nANSWER: ", 1)
                    topic = metadata.get("topic", "")
                    question = parts[0].replace("QUESTION: ", "") if len(parts) > 0 else ""
                    answer = parts[1] if len(parts) > 1 else doc
                    
                # Get tags as list
                tags = metadata.get("tags", "").split(",") if metadata.get("tags") else []
                
                # Create result object with no score
                faq_result = FAQSearchResult(
                    id=metadata.get("id", ""),
                    topic=topic or metadata.get("topic", ""),
                    question=question,
                    answer=answer,
                    tags=tags,
                    score=0.0,  # No scoring for empty queries
                    source=metadata.get("source", ""),
                    last_updated=datetime.fromisoformat(metadata.get("last_updated", datetime.utcnow().isoformat()))
                )
                faq_results.append(faq_result)
            
            query_time_ms = (time.time() - start_time) * 1000
            logger.info(f"FAQ search with empty query found {len(faq_results)} results in {query_time_ms:.2f}ms")
                
            return len(faq_results), faq_results, query_time_ms
        
        # For semantic search, generate embedding
        query_embedding = await self.embedder.generate_embedding_async(search_text)
        
        # Verify embedding is not empty/zero
        if not any(query_embedding):
            logger.warning(f"Generated a zero embedding for query: '{search_text}'")
        else:
            logger.info(f"Generated embedding with {len(query_embedding)} dimensions for query: '{search_text}'")
        
        # Add debugging to log the actual query params
        logger.info(f"Searching with embedding, n_results={search_query.limit}, where={where_clause}")
        
        # Search collection using the embedding 
        results = await self.chroma.search(
            collection_name=self.collection_name,
            query="",  # Empty string since we're using embedding
            query_embedding=query_embedding,  # This will be used instead
            n_results=search_query.limit,
            where=where_clause
        )
        
        # Debug distances to see what's coming back
        if results.distances:
            logger.info(f"Got {len(results.distances)} results with distances: {results.distances[:5]}")
        else:
            logger.warning("No distances returned from search")
        
        # Process results
        faq_results = []
        for i, (doc, metadata, distance) in enumerate(zip(results.documents, results.metadatas, results.distances)):
            # Convert distance to similarity score (1 - distance)
            # In ChromaDB, distance is usually between 0-2 for cosine distance
            # so we need to ensure we get a score between 0-1
            similarity = max(0.0, min(1.0, 1.0 - 0.5 * distance))
            
            # Log the distance and calculated similarity for debugging
            logger.info(f"Result {i}: distance={distance}, similarity={similarity}")
            
            # Skip results below minimum score
            if similarity < search_query.min_score:
                logger.info(f"Skipping result with similarity {similarity} below min_score {search_query.min_score}")
                continue
                
            # Extract question and answer from document
            try:
                parts = doc.split("\n")
                topic = parts[0].replace("TOPIC: ", "") if parts[0].startswith("TOPIC: ") else ""
                question = parts[1].replace("QUESTION: ", "") if parts[1].startswith("QUESTION: ") else ""
                answer = parts[2].replace("ANSWER: ", "") if len(parts) > 2 and parts[2].startswith("ANSWER: ") else ""
            except IndexError:
                # Fallback for legacy data format
                parts = doc.split("\nANSWER: ", 1)
                topic = metadata.get("topic", "")
                question = parts[0].replace("QUESTION: ", "") if len(parts) > 0 else ""
                answer = parts[1] if len(parts) > 1 else doc
                
            # Get tags as list
            tags = metadata.get("tags", "").split(",") if metadata.get("tags") else []
            
            # Create result object
            faq_result = FAQSearchResult(
                id=metadata.get("id", ""),
                topic=topic or metadata.get("topic", ""),
                question=question,
                answer=answer,
                tags=tags,
                score=similarity,
                source=metadata.get("source", ""),
                last_updated=datetime.fromisoformat(metadata.get("last_updated", datetime.utcnow().isoformat()))
            )
            faq_results.append(faq_result)
        
        query_time_ms = (time.time() - start_time) * 1000
        logger.info(f"FAQ search for '{search_query.query}' found {len(faq_results)} results in {query_time_ms:.2f}ms")
            
        return len(faq_results), faq_results, query_time_ms
        
    async def get_faq(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """Get an FAQ item by ID"""
        result = await self.chroma.get(
            collection_name=self.collection_name,
            ids=[faq_id]
        )
        
        if not result.documents or len(result.documents) == 0:
            return None
            
        document = result.documents[0]
        metadata = result.metadatas[0]
        
        # Parse document based on format
        try:
            parts = document.split("\n")
            topic = parts[0].replace("TOPIC: ", "") if parts[0].startswith("TOPIC: ") else ""
            question = parts[1].replace("QUESTION: ", "") if parts[1].startswith("QUESTION: ") else ""
            answer = parts[2].replace("ANSWER: ", "") if len(parts) > 2 and parts[2].startswith("ANSWER: ") else ""
        except IndexError:
            # Fallback for legacy data format
            parts = document.split("\nANSWER: ", 1)
            topic = metadata.get("topic", "")
            question = parts[0].replace("QUESTION: ", "") if len(parts) > 0 else ""
            answer = parts[1] if len(parts) > 1 else document
        
        # Get tags as list
        tags = metadata.get("tags", "").split(",") if metadata.get("tags") else []
        
        return {
            "id": metadata.get("id", faq_id),
            "topic": topic or metadata.get("topic", ""),
            "question": question,
            "answer": answer,
            "tags": tags,
            "source": metadata.get("source", ""),
            "is_published": metadata.get("is_published", True),
            "priority": metadata.get("priority", 0),
            "created_by": metadata.get("created_by"),
            "last_updated": metadata.get("last_updated", datetime.utcnow().isoformat())
        }
        
    async def update_faq(self, faq_id: str, faq_update: Dict[str, Any]) -> bool:
        """Update an existing FAQ item"""
        # Get current FAQ
        current_faq = await self.get_faq(faq_id)
        if not current_faq:
            return False
            
        # Update fields
        updated_faq = {**current_faq}
        for key, value in faq_update.items():
            if value is not None:
                updated_faq[key] = value
                
        # Create new document
        new_document = f"TOPIC: {updated_faq['topic']}\nQUESTION: {updated_faq['question']}\nANSWER: {updated_faq['answer']}"
        
        # Convert any list types to strings for ChromaDB compatibility
        tags_string = ",".join(updated_faq["tags"]) if updated_faq["tags"] else ""
        
        # Update metadata
        new_metadata = {
            "id": faq_id,
            "topic": updated_faq["topic"],
            "question": updated_faq["question"],
            "tags": tags_string,
            "is_published": updated_faq["is_published"],
            "priority": updated_faq["priority"],
            "source": updated_faq["source"],
            "created_by": updated_faq.get("created_by", "system"),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Generate new embedding
        new_embedding = await self.embedder.generate_embedding_async(new_document)
        
        # Update in collection
        await self.chroma.update(
            collection_name=self.collection_name,
            ids=[faq_id],
            documents=[new_document],
            metadatas=[new_metadata],
            embeddings=[new_embedding]
        )
        
        logger.info(f"Updated FAQ item with ID: {faq_id}")
        return True
        
    async def delete_faq(self, faq_id: str) -> bool:
        """Delete an FAQ item"""
        try:
            await self.chroma.delete(
                collection_name=self.collection_name,
                ids=[faq_id]
            )
            logger.info(f"Deleted FAQ item with ID: {faq_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting FAQ {faq_id}: {str(e)}")
            return False
            
    async def get_topics(self) -> List[str]:
        """Get all unique topics from FAQ collection"""
        try:
            return await self.chroma.get_metadata_keys(self.collection_name, "topic")
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            return []
            
    async def get_sources(self) -> List[str]:
        """Get all unique sources from FAQ collection"""
        try:
            return await self.chroma.get_metadata_keys(self.collection_name, "source")
        except Exception as e:
            logger.error(f"Error getting sources: {str(e)}")
            return []
            
    async def import_jsonl(self, file_path: str, user_id: str) -> Tuple[int, List[Dict[str, Any]]]:
        """Import FAQs from a JSONL file"""
        successful_imports = 0
        failed_imports = []
        
        try:
            # Try to detect encoding - include UTF-16 formats
            encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']
            file_content = None
            
            # First, try to detect encoding using binary reading
            detected_encoding = None
            with open(file_path, 'rb') as f:
                raw_data = f.read(4)  # Read first 4 bytes to check BOM
                if raw_data.startswith(b'\xff\xfe'):
                    detected_encoding = 'utf-16-le'
                    logger.info(f"Detected UTF-16-LE BOM marker")
                elif raw_data.startswith(b'\xfe\xff'):
                    detected_encoding = 'utf-16-be'
                    logger.info(f"Detected UTF-16-BE BOM marker")
                elif raw_data.startswith(b'\xef\xbb\xbf'):
                    detected_encoding = 'utf-8-sig'
                    logger.info(f"Detected UTF-8 BOM marker")
            
            # Try detected encoding first, then fallback to others
            if detected_encoding:
                encodings.insert(0, detected_encoding)
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        file_content = f.read()
                    logger.info(f"Successfully read file with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    logger.warning(f"Failed to decode with encoding: {encoding}")
                    continue
            
            if file_content is None:
                raise ValueError("Unable to decode file with any supported encoding")
            
            # Process each line
            for line_number, line in enumerate(file_content.splitlines(), 1):
                if not line.strip():
                    continue
                    
                try:
                    # Parse JSON
                    faq_data = json.loads(line)
                    
                    # Validate against model
                    faq_item = JSONLImportItem(**faq_data)
                    
                    # Create FAQ item
                    full_faq = FAQItem(
                        topic=faq_item.topic,
                        question=faq_item.question,
                        answer=faq_item.answer,
                        tags=faq_item.tags,
                        source=faq_item.source,
                        created_by=user_id,
                        is_published=True
                    )
                    
                    # Add to database
                    faq_id = await self.add_faq(full_faq, user_id)
                    successful_imports += 1
                    logger.info(f"Imported FAQ #{successful_imports}: {faq_item.question[:30]}...")
                    
                except Exception as e:
                    # Log the error and continue with next item
                    error_detail = {
                        "line": line_number,
                        "content": line[:100] + "..." if len(line) > 100 else line,
                        "error": str(e)
                    }
                    logger.error(f"Error importing FAQ at line {line_number}: {str(e)}")
                    failed_imports.append(error_detail)
                    
            return successful_imports, failed_imports
            
        except Exception as e:
            logger.error(f"Error importing JSONL file: {str(e)}")
            raise 