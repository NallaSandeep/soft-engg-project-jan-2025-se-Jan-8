# FAQ Agent Implementation with Fallback Mechanisms

## Overview

The FAQ Agent is responsible for retrieving relevant FAQ entries from the StudyIndexer service in response to user queries. This document outlines the implementation of a robust FAQ Agent with multi-tier fallback mechanisms to ensure users receive helpful responses even when the primary API encounters issues.

## Current Implementation

Currently, the FAQ retrieval process:
1. Takes a user query
2. Makes a direct API call to the StudyIndexer FAQ search endpoint
3. Returns the results to the supervisor for response generation
4. Has limited error handling - if the API fails, the response may be empty or error-prone

## Enhanced Implementation

The enhanced FAQ Agent will implement a tiered fallback strategy:

### Tier 1: Semantic Search via API (Primary Method)
- Use the StudyIndexer's `/api/v1/faq/search` endpoint
- Leverage vector search with embeddings for semantic matching
- Apply filtering by topic, tags, or source if specified

### Tier 2: Keyword Matching on Cached Data (First Fallback)
- Maintain a local cache of FAQ data in JSON format
- Implement a simple but effective keyword matching algorithm
- Support similar filtering capabilities as the primary method
- Use when the API call fails or returns no results

### Tier 3: LLM Generation (Final Fallback)
- When both semantic search and keyword matching fail
- Allow the LLM to generate an answer based on its knowledge
- Include a disclaimer indicating the response is not from official FAQs
- Still maintain a consistent response format

## Implementation Details

### 1. Creating the Enhanced FAQ Agent

```python
# faq_agent.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent
from .config import Config

class FAQAgent(BaseAgent):
    """Agent for retrieving FAQs with robust fallback mechanisms."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_file = Path("data/cached_faqs.json")
        self.cached_faqs = self._load_cached_faqs()
        self.min_semantic_score = 0.5  # Minimum score for semantic search results
        self.min_keyword_score = 0.2   # Minimum score for keyword matching
        
    def _load_cached_faqs(self) -> List[Dict[str, Any]]:
        """Load FAQ data from cache file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.warning(f"Failed to load cached FAQs: {str(e)}")
            return []
    
    async def update_cache(self) -> None:
        """Update the local FAQ cache from the API."""
        try:
            # Get all topics to query each topic separately
            topics_response = await self.make_http_request(
                method="GET",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/faq/topics"
            )
            
            all_faqs = []
            if topics_response.get("success", False):
                topics = topics_response.get("data", {}).get("topics", [])
                
                # Query each topic to get all FAQs
                for topic in topics:
                    response = await self.make_http_request(
                        method="POST",
                        url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/faq/search",
                        json={"query": "", "topic": topic, "min_score": 0}
                    )
                    
                    if response.get("success", False):
                        all_faqs.extend(response.get("results", []))
            
            # Save to cache file
            if all_faqs:
                self.cache_file.parent.mkdir(exist_ok=True)
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(all_faqs, f, ensure_ascii=False, indent=2)
                self.cached_faqs = all_faqs
                logging.info(f"Updated FAQ cache with {len(all_faqs)} entries")
                
        except Exception as e:
            logging.error(f"Failed to update FAQ cache: {str(e)}")
    
    async def search_faqs(self, query: str, topic: Optional[str] = None, 
                           tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for FAQs with tiered fallback strategy.
        
        Args:
            query: The user's question
            topic: Optional topic filter
            tags: Optional tags filter
            
        Returns:
            Dict containing results and metadata
        """
        # Tier 1: Try semantic search via API
        api_results = await self._semantic_search(query, topic, tags)
        
        if api_results.get("results"):
            return {
                "results": api_results["results"],
                "source": "semantic_search",
                "query": query
            }
        
        # Tier 2: Try keyword matching on cached data
        logging.info("API search returned no results, using keyword fallback")
        keyword_results = self._keyword_search(query, topic, tags)
        
        if keyword_results.get("results"):
            return {
                "results": keyword_results["results"],
                "source": "keyword_fallback",
                "query": query
            }
        
        # Tier 3: Prepare for LLM-based response
        logging.info("All FAQ search methods failed, preparing LLM response")
        return {
            "results": [],
            "use_llm_knowledge": True,
            "query": query,
            "fallback_message": "No specific FAQ matched your question. Generating response from general knowledge."
        }
    
    async def _semantic_search(self, query: str, topic: Optional[str] = None, 
                              tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform semantic search via StudyIndexer API."""
        try:
            search_params = {
                "query": query,
                "min_score": self.min_semantic_score
            }
            
            if topic:
                search_params["topic"] = topic
                
            if tags:
                search_params["tags"] = tags
                
            response = await self.make_http_request(
                method="POST",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/faq/search",
                json=search_params
            )
            
            if response.get("success", False):
                return {"results": response.get("results", [])}
            
            return {"results": []}
            
        except Exception as e:
            logging.error(f"Error in semantic search: {str(e)}")
            return {"results": []}
    
    def _keyword_search(self, query: str, topic: Optional[str] = None, 
                       tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform keyword matching on cached FAQs."""
        if not self.cached_faqs:
            return {"results": []}
            
        # Prepare query for matching
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        matches = []
        for faq in self.cached_faqs:
            # Apply filters if specified
            if topic and faq.get("topic") != topic:
                continue
                
            if tags and not any(tag in faq.get("tags", []) for tag in tags):
                continue
            
            # Calculate word overlap score
            question_lower = faq["question"].lower()
            question_words = set(question_lower.split())
            
            # Include topic and tags in the matching
            topic_words = set(faq.get("topic", "").lower().split())
            tag_words = set(word for tag in faq.get("tags", []) for word in tag.lower().split())
            
            # Calculate total text for matching
            searchable_text = question_words.union(topic_words).union(tag_words)
            
            # Calculate overlap
            # More sophisticated matching could use TF-IDF or other techniques
            overlap = len(query_words.intersection(searchable_text))
            score = overlap / max(1, len(query_words))  # Avoid division by zero
            
            if score >= self.min_keyword_score:
                matches.append({
                    "id": faq.get("id", "unknown"),
                    "topic": faq.get("topic", ""),
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "tags": faq.get("tags", []),
                    "score": score,
                    "source": faq.get("source", "unknown"),
                    "matched_by": "keyword_fallback"
                })
        
        # Sort by score and return top results
        matches.sort(key=lambda x: x["score"], reverse=True)
        return {"results": matches[:5]}  # Limit to top 5 matches
```

### 2. Updating the Workflow

```python
# workflow.py (excerpt)
def create_workflow():
    """Create the agent workflow graph with fallback handling."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("check_question_type", check_question_type_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("faq_agent", faq_agent_node)  # Updated node
    workflow.add_node("course_identifier", course_identifier_node)
    workflow.add_node("course_content", course_content_node)
    workflow.add_node("dismiss", dismiss_node)
    
    # Set entry point
    workflow.set_entry_point("check_question_type")
    
    # Define edges
    # ...
    
    return workflow.compile(checkpointer=MemorySaver())
```

### 3. Creating the FAQ Agent Node

```python
# nodes/faq_agent_node.py
from typing import Dict, Any

from langchain.schema import AgentAction

from ..agents.faq_agent import FAQAgent
from ..utils.state import AgentState

async def faq_agent_node(state: AgentState) -> AgentState:
    """Node for FAQ agent with fallback handling."""
    metadata = state.get("metadata", {})
    query = metadata.get("original_query", "")
    
    # Create FAQ agent
    agent = FAQAgent()
    
    # Check if cache needs to be refreshed (can be done periodically)
    # This could be triggered by a config setting or time-based condition
    if state.get("refresh_faq_cache", False):
        await agent.update_cache()
    
    # Search FAQs with fallback mechanisms
    search_results = await agent.search_faqs(query)
    
    # Process results into a consistent format for the supervisor
    if search_results.get("use_llm_knowledge", False):
        # Prepare for LLM fallback
        state["context"] = {
            "findings": [{
                "type": "faq_fallback",
                "query": query,
                "message": search_results.get("fallback_message", ""),
                "use_llm_knowledge": True
            }]
        }
    else:
        # Process normal or keyword fallback results
        results = search_results.get("results", [])
        source = search_results.get("source", "unknown")
        
        state["context"] = {
            "findings": [{
                "type": "faq",
                "query": query,
                "results": results,
                "source": source,
                "count": len(results)
            }]
        }
    
    # Set next step to supervisor
    state["next_step"] = "supervisor"
    return state
```

### 4. Updating the Supervisor for Handling FAQ Fallback Responses

```python
# Updated method in supervisor_class.py
async def generate_final_response(self, state: AgentState) -> str:
    """Generate a final response with proper fallback handling."""
    # Extract the original query and context
    original_query = state["metadata"].get("original_query", "")
    context = state["context"]
    
    # Check if we need to use LLM fallback
    use_llm_knowledge = False
    findings = context.get("findings", [])
    
    for finding in findings:
        if finding.get("use_llm_knowledge", False):
            use_llm_knowledge = True
            break
    
    # Create special prompt for LLM fallback if needed
    if use_llm_knowledge:
        if any(finding.get("type") == "faq_fallback" for finding in findings):
            # FAQ-specific fallback prompt
            prompt = self._create_faq_fallback_prompt(original_query)
        else:
            # General fallback prompt
            prompt = self._create_general_fallback_prompt(original_query, findings)
    else:
        # Use normal prompt with available research findings
        prompt = get_response_synthesis_prompt(
            original_query=original_query,
            context=self._format_context(context)
        )
    
    # Generate the response
    chain = self.create_chain(prompt)
    response = await chain.ainvoke({})
    
    return response

def _create_faq_fallback_prompt(self, query: str) -> str:
    """Create a prompt for FAQ-specific LLM fallback."""
    return f"""Answer the following question based on your knowledge:
Question: {query}

No specific FAQ entries were found for this question. Please provide a helpful response
based on your knowledge of common academic policies, procedures, and best practices.

Format your response as if you are an academic advisor or student support staff member.
Begin with a brief, direct answer, followed by any necessary explanation or context.

Important: Clarify that this information is general guidance and the student should 
consult their specific institutional policies or academic advisors for definitive answers.
"""
```

## Usage and Maintenance

### Regular Cache Updates
The FAQ cache should be updated regularly to ensure the fallback mechanism has access to the latest FAQ data. This can be done:

1. On system startup
2. On a scheduled basis (e.g., daily)
3. When triggered by an admin action

### Monitoring and Improvement
To continually improve the FAQ Agent:

1. Log when fallbacks are triggered to identify patterns
2. Track which keywords are most commonly used in successful matches
3. Analyze questions that fail all tiers to identify gaps in the FAQ database

### Sample Configuration

```python
# config.py
class FAQAgentConfig:
    CACHE_PATH = "data/cached_faqs.json"
    MIN_SEMANTIC_SCORE = 0.5
    MIN_KEYWORD_SCORE = 0.2
    MAX_RESULTS = 5
    CACHE_REFRESH_INTERVAL_HOURS = 24
```

## Integration Testing

### Test Cases
1. API returns good results - verify primary path works
2. API returns no results - verify keyword fallback works
3. API throws exception - verify keyword fallback handles errors
4. No matching FAQs found - verify LLM fallback works
5. Topic/tag filtering - verify filters work in all tiers 