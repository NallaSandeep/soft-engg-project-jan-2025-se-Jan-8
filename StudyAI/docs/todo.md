# StudyAI Improvements: Requirements & Implementation Plan

## Current System Analysis

### Architecture Overview
StudyAI is a multi-agent chat platform using LangGraph (from LangChain ecosystem) that orchestrates specialized agents to handle student questions:

- Uses Google's Gemini model via ChatGoogleGenerativeAI
- Implements a directed state graph for routing queries between agents
- Integrates with StudyIndexer service for retrieval-augmented generation (RAG)
- Can decompose complex queries into subquestions and synthesize answers

### Key Components
- `BaseAgent`: Foundation class with HTTP and LLM functionality
- `StateGraph`: Manages conversation flow between agent nodes
- Main agent types:
  - `QuestionTypeChecker`: Filters inappropriate/generic questions
  - `Supervisor`: Routes questions and orchestrates workflow
  - `RagAgent`: Handles FAQ lookups 
  - `CourseGuideAgent`: Retrieves course information and content

### Identified Issues
1. **Excessive Hardcoding**:
   - Extensive mock data in `course_guide_class.py`
   - Fixed prompts in `prompts.py`
   - Static routing logic
   - Limited configuration options

2. **Architecture Misalignment**:
   - `CourseGuideAgent` combines both course identification and content retrieval
   - No clear separation between searching for course codes and retrieving course content
   - Direct API calls inside agents rather than separation of concerns

3. **Limited Fallback Mechanisms**:
   - Insufficient error handling when StudyIndexer APIs fail
   - No structured alternative when content can't be found
   - Similar issue with FAQ search API that needs fallback handling

## Proper Implementation Flow

The correct implementation flow should be:

1. User sends message via WebSocket
2. Message processed by `check_question_type_node`
3. If appropriate, routes to `supervisor_node`
4. Supervisor may decompose complex questions
5. Routes to specialized agents:
   - `faq_agent` → StudyIndexer FAQ search endpoint
   - `course_guide_agent` → StudyIndexer Course Selector API
6. With course code(s) identified, query StudyIndexer Course Content Search API
7. Final response synthesized and streamed back to user

## Enhancement Requirements

### 1. Separation of Course Identification and Content Retrieval
- Split `CourseGuideAgent` into two distinct components:
  - `CourseIdentificationAgent`: Uses course-selector API to find course codes
  - `CourseContentAgent`: Uses course-content API to fetch content for identified courses
- Update workflow graph to reflect this sequential process

### 2. Fallback Mechanism for Course APIs
- When StudyIndexer APIs fail or return insufficient data:
  - Use hardcoded keyword-to-course mapping for course identification
  - When content retrieval fails, instruct LLM to answer from its knowledge
  - Maintain citation structure even in fallback mode

### 3. Improved FAQ Agent with Fallback Mechanism
- Enhance the `FAQAgent` to handle API failures gracefully:
  - Primary path: Call StudyIndexer FAQ search API for semantic search
  - Fallback path 1: Use keyword matching against cached FAQ data when semantic search fails
  - Fallback path 2: Allow LLM to generate answers with appropriate disclaimers when no FAQ matches
- Include support for topic/tags filtering in fallback
- Maintain consistent response format between primary and fallback paths

### 4. Improved Response Formatting
- Implement standardized citation format
- Include source information from course content
- Structure responses with clear sections

## Implementation Plan

### Phase 1: Refactoring CourseGuideAgent
1. Create new files:
   - `course_identification_agent.py`
   - `course_content_agent.py`
   - `fallback_data.py` (for hardcoded keyword mappings)

2. Implement `CourseIdentificationAgent`:
   - Call course-selector API with proper error handling
   - Fall back to keyword mapping when API fails
   - Standardize response format

3. Implement `CourseContentAgent`:
   - Accept course codes from identification agent
   - Call course-content API with proper error handling
   - Support LLM fallback with citation data

4. Update workflow in `workflow.py`:
   - Add new nodes for each specialized agent
   - Configure proper routing between them

### Phase 2: Enhancing FAQ Agent
1. Refactor `rag_agent.py` for better error handling:
   - Add try/except blocks around API calls
   - Implement tiered fallback strategy
   - Support caching of FAQ data for offline use

2. Create `faq_fallback_data.py`:
   - Define keyword mapping structure for FAQs
   - Implement simple keyword matching algorithm
   - Provide utility methods for filtering and ranking results

3. Update the FAQ search method:
```python
async def search_faq(self, query: str):
    """Search FAQs with fallback mechanisms."""
    try:
        # First attempt: API-based semantic search
        response = await self.make_http_request(
            method="POST",
            url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/faq/search",
            json={"query": query, "min_score": 0.5}
        )
        
        # Check if API call was successful and returned results
        if response.get("success", False) and response.get("results", []):
            return self._format_api_response(response)
        
        # If empty results or error, fall back to keyword matching
        logging.info("FAQ search API returned no results, using keyword fallback")
        return self._use_keyword_fallback(query)
        
    except Exception as e:
        logging.error(f"Error calling FAQ search API: {str(e)}")
        # Use fallback on exception
        return self._use_keyword_fallback(query)
        
    # If keyword fallback also fails, prepare for LLM-based response
    logging.info("All FAQ search methods failed, preparing LLM response")
    return {
        "results": [],
        "use_llm_knowledge": True,
        "query": query,
        "fallback_message": "No specific FAQ matched your question. Generating response from general knowledge."
    }
```

### Phase 3: Enhancing Supervisor & Response Generation
1. Update `supervisor_class.py`:
   - Add specialized handling for LLM fallback scenarios
   - Enhance `generate_final_response` method to support fallback content
   - Implement citation processing

2. Improve prompts in `prompts.py`:
   - Add citation instructions
   - Support LLM fallback scenarios
   - Standardize response formatting

### Phase 4: Testing & Refinement
1. Test with various query types:
   - FAQ questions
   - Course-specific questions
   - Questions requiring fallback
   - Complex multi-part questions

2. Refine based on real-world usage:
   - Update keyword mappings
   - Adjust fallback thresholds
   - Enhance prompts based on response quality

## Detailed Implementation Notes

### CourseIdentificationAgent
```python
class CourseIdentificationAgent(BaseAgent):
    """Agent that identifies relevant courses with fallback."""
    
    async def get_relevant_courses(self, query: str, limit: int = 4):
        """Call course-selector API with fallback to hardcoded data."""
        try:
            # First try API call
            response = await self.make_http_request(
                method="POST",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/course-selector/search",
                json={"query": query, "limit": limit, "subscribed_courses": ["SE101", "MAD201", "DBMS101", "BA201"]}
            )
            
            # Check if API call was successful and returned results
            if response.get("success", False) and response.get("data", {}).get("results", []):
                return self._format_api_response(response)
            
            # If empty results or error, fall back to hardcoded logic
            logging.info("Course selector API returned no results, using fallback")
            return self._use_fallback_data(query)
            
        except Exception as e:
            logging.error(f"Error calling course-selector API: {str(e)}")
            # Use fallback on exception
            return self._use_fallback_data(query)
```

### FAQAgent with Fallback
```python
class FAQAgent(BaseAgent):
    """Agent for FAQ retrieval with fallback mechanisms."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load cached FAQs for fallback
        self.cached_faqs = self._load_cached_faqs()
        
    def _load_cached_faqs(self):
        """Load FAQ data from cache file."""
        try:
            with open("cached_faqs.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("Failed to load cached FAQs")
            return []
            
    async def _use_keyword_fallback(self, query):
        """Use keyword matching to find relevant FAQs."""
        if not self.cached_faqs:
            return {"results": []}
            
        # Simple keyword matching algorithm
        matches = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for faq in self.cached_faqs:
            # Calculate simple word overlap score
            question_lower = faq["question"].lower()
            question_words = set(question_lower.split())
            
            # Check both question and tags
            tags = set(tag.lower() for tag in faq.get("tags", []))
            
            # Calculate overlap score
            overlap = len(query_words.intersection(question_words.union(tags)))
            if overlap > 0:
                matches.append({
                    "id": faq.get("id", "unknown"),
                    "topic": faq.get("topic", ""),
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "tags": faq.get("tags", []),
                    "score": overlap / len(query_words),  # Normalize score
                    "source": faq.get("source", "unknown"),
                    "matched_by": "keyword_fallback"
                })
        
        # Sort by score and limit results
        matches.sort(key=lambda x: x["score"], reverse=True)
        return {"results": matches[:5]}
```

### CourseContentAgent
```python
class CourseContentAgent(BaseAgent):
    """Agent that retrieves course content with fallback to LLM."""
    
    async def get_course_content(self, course_ids: List[str], query: str):
        """Call course-content API with fallback to LLM."""
        try:
            # First try API call
            response = await self.make_http_request(
                method="GET",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/course-content/search",
                params={"query": query, "course_ids": ",".join(course_ids), "limit": 10}
            )
            
            # Check if API call was successful and returned results
            if response.get("success", False) and response.get("data", {}).get("content_chunks", []):
                return self._format_api_response(response)
            
            # If empty results or error, prepare for LLM fallback
            logging.info("Course content API returned no results, preparing LLM fallback")
            return self._prepare_llm_fallback(course_ids, query)
            
        except Exception as e:
            logging.error(f"Error calling course-content API: {str(e)}")
            # Prepare for LLM fallback on exception
            return self._prepare_llm_fallback(course_ids, query)
```

### Updated Workflow
```python
def create_workflow():
    """Create the agent workflow graph with fallback handling."""
    workflow = StateGraph(AgentState)
    
    # Add nodes with enhanced fallback logic
    workflow.add_node("check_question_type", check_question_type_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("faq_agent", rag_agent_node)
    workflow.add_node("course_identifier", course_identifier_node)  # New specialized node
    workflow.add_node("course_content", course_content_node)  # New specialized node
    workflow.add_node("dismiss", dismiss_node)
    
    # Sequential processing from identifier to content
    workflow.add_edge("course_identifier", "course_content")
    workflow.add_edge("course_content", "supervisor")
    
    # Other edges...
    
    return workflow.compile(checkpointer=MemorySaver())
```

## Next Steps

1. Implement core refactoring:
   - [x] Document current architecture
   - [ ] Create `course_identification_agent.py`
   - [ ] Create `course_content_agent.py`
   - [ ] Create `fallback_data.py`
   - [ ] Enhance `rag_agent.py` with FAQ fallback

2. Update workflow:
   - [ ] Modify `workflow.py` to include new agents
   - [ ] Update routing logic in `supervisor.py`
   - [ ] Enhance prompts in `prompts.py`

3. Add robust error handling:
   - [ ] Implement fallback logic for course identification
   - [ ] Implement fallback for FAQ search
   - [ ] Implement LLM fallback for content retrieval
   - [ ] Add citation generation for fallback content

4. Testing and refinement:
   - [ ] Test with various query types
   - [ ] Adjust fallback thresholds
   - [ ] Refine prompts and response formatting 