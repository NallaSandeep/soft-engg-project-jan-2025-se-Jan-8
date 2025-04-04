Below is a deep, file-by-file overview of how the StudyAI module works, how it connects to the studyindexer service for retrieval-augmented generation (RAG), and how it orchestrates multi-agent flows for query handling. I will take you through each file in the approximate order you would read them when exploring this architecture for the first time. Use the headings as a reference structure.

--------------------------------------------------------------------------------
1. Top-Level Files
--------------------------------------------------------------------------------

1.1 README.md (StudyAI/README.md)  
   • Describes the StudyAI service as part of the “StudyHub” platform, aiming to offer an AI-based study assistant.  
   • Lists prerequisites (Python ≥ 3.11, Google Gemini API key, LangSmith for LangChain).  
   • Outlines how to install dependencies, set up the environment variables, and run the server (FastAPI + Uvicorn).  
   • Mentions key endpoints like POST /chat/session, WS /stream/chat/session/{session_id}/message, etc.  
   • Mentions the project structure:  
     studyai/  
     ├── app.py (FastAPI entry point)  
     ├── config.py (Handles environment variables)  
     ├── requirements.txt  
     ├── src/  
     └── more files/folders  

   Although not always fully up-to-date or comprehensive, it gives you a sense that this is a FastAPI-based application providing a chat interface that integrates with external LLMs and a local RAG store (studyindexer).

1.2 config.py  
   • Loads environment variables via python-dotenv.  
   • Defines class Config that captures:  
       – GEMINI_API_KEY (required for the Google Generative AI)  
       – LANGSMITH_API_KEY (for LangChain analytics)  
       – A variety of other toggles: LANGSMITH_TRACING, RATE_LIMIT_ENABLED, etc.  
       – SQLALCHEMY_DATABASE_URI for the database.  
       – A STUDY_INDEXER_PORT that’s used to contact the external “studyindexer” service.  
   • Has a validate_config method that checks whether required environment variables (like GEMINI_API_KEY, LANGSMITH_API_KEY) are actually populated.  

1.3 app.py  
   • Main FastAPI application file. Creates and configures the FastAPI app.  
   • startup/shutdown events are handled in an asynccontextmanager named lifespan:  
       – At startup, checks if required config variables are set  
       – Tries to enable an in-memory LangChain cache if enabled by the config  
       – On shutdown, closes any open WebSocket connections via disconnect_all_clients  
   • The application sets up:  
       – A GZipMiddleware  
       – Rate limiting via SlowAPI if RATE_LIMIT_ENABLED is true  
       – A single router from src.routes.basic_routes and src.routes.websocket_routes  
   • Exports a final app = create_application()

1.4 database.py  
   • Creates a SQLAlchemy engine using the Config.SQLALCHEMY_DATABASE_URI.  
   • sessionmaker = SessionLocal for obtaining DB sessions within API routes or services.  
   • init_db function: calls Base.metadata.create_all to create tables if they do not exist.  
   • get_db_session / get_db are context managers for retrieving a session in a safe manner, handling commits, rollbacks, etc.

--------------------------------------------------------------------------------
2. The “src/core” Directory
--------------------------------------------------------------------------------
These files define the core “agentic workflow” logic and shared data structures.

2.1 core/__init__.py  
   • Empty file that just marks the directory as a Python package.

2.2 base.py  
   • Defines BaseAgent, which sets up a generic pattern for building specialized service “agents.”  
   • A BaseAgent can:  
       – Load the language model (ChatGoogleGenerativeAI) using environment settings (model_name, temperature, Google API key).  
       – Create a “chain” from a ChatPromptTemplate → LLM → output_parser.  
       – Format responses with some metadata (model, temperature).  
       – Make HTTP requests to external services with built-in error handling.  
   • This is then subclassed by specialized “agents” (e.g. CourseGuideAgent, RagAgent, etc.).

2.3 state.py  
   • Defines typed dictionaries and helper functions for storing “AgentState.”  
   • AgentState holds:  
       – messages: an array of user or AI messages  
       – context: a dictionary with topic/query/sources/findings  
       – next_step: a string like “supervisor,” “dismiss,” etc., telling the workflow what node to go to next  
   • Provides convenience functions:
       – initialize_state  
       – update_metadata  
       – add_research_source  
       – add_research_finding  
       – etc.  
   • This data structure is updated by each agent node to keep track of the conversation flow.

2.4 workflow.py  
   • Houses create_workflow, the main “StateGraph.”  
   • Uses langgraph’s StateGraph to define a node-based chain of execution:  
       – Entry point is check_question_type (q_type_checker).  
       – Then it can route to “supervisor,” which itself can route to “faq_agent,” “course_guide_agent,” or “dismiss.”  
       – “faq_agent” (rag_agent_node) or “course_guide_agent” (course_guide_node) do the retrieval logic.  
       – They bounce back to “supervisor” when done, until the pipeline ends (END).  
   • The result is a robust multi-agent orchestration: subquestions, re-routing, etc.  

--------------------------------------------------------------------------------
3. The “src/models” Directory
--------------------------------------------------------------------------------
3.1 src/models/db_models.py  
   • Declares SQLAlchemy ORM models:  
       – User, Message, ChatSession, ReportedResponse  
   • Provides Pydantic models for input/output:  
       – MessageCreate, MessageResponse, ChatSessionResponse, etc.  
   • This is how the system stores chat logs, user sessions, and reported responses in the database.

3.2 src/models/websocket_models.py  
   • Simple Pydantic models for WebSocket-level messaging (ChatMessage, ChatResponse).  
   • This is used by the streaming chat endpoints.

3.3 src/models/__init__.py  
   • Empty marker file.

--------------------------------------------------------------------------------
4. The “src/modules” Directory: Agents and Nodes
--------------------------------------------------------------------------------
These are the specialized agent classes and node implementations that handle various user queries.

4.1 course_guide_class.py  
   • Defines the CourseGuideAgent.  
   • Subclasses BaseAgent to focus on course content queries.  
   • get_relevant_courses: optionally calls the external studyindexer “/course-selector/search” endpoint if use_mock_data is False, or returns “mock_courses” if use_mock_data is True.  
   • get_course_content: fetches or mocks data for deeper topic coverage.  
   • get_courses_with_content: a single function to fetch relevant courses plus their content. Also includes some partial integrity-check logic (commented out), showing how it might handle assignment questions with warnings.

4.2 course_guide.py  
   • Contains the course_guide_node, which is part of the StateGraph.  
   • This node:  
       – Creates a CourseGuideAgent  
       – Finds relevant courses and course content for the user’s query.  
       – May handle special logic for academic assignments (like an “is_integrity_violation” check).  
       – Adds the results (findings) into the AgentState’s context object.

4.3 faq_agent.py  
   • Defines the RagAgent (also a subclass of BaseAgent).  
   • Lash up to “get_relevant_docs,” which calls the “/faq/search” route of the studyindexer to retrieve top FAQ documents.  
   • The rag_agent_node function:  
       – Creates a RagAgent, processes the query, retrieves relevant FAQ context, and appends the results to the state’s “findings.”  
   • If no FAQ doc is found, it suggests the user try the “course guide” agent.

4.4 q_type_checker.py  
   • The first node in the workflow.  
   • The agent is a small LLM-based checker that decides if the question is “Inappropriate,” “Generic,” or “Other” by analyzing the text.  
   • If the question is “Inappropriate” or “Generic,” the node sets next_step to “dismiss” so that the user is gently turned away or asked to clarify.

4.5 dismiss_node.py  
   • The node that “dismisses” queries.  
   • It picks a reason from the last system message and returns an appropriate AI response: e.g. “Inappropriate content” or “Hello, I am designed for academic questions,” etc.

4.6 integerity_tool.py  
   • Another agent, IntegrityChecker, that can call an “/integrity-check/check” endpoint on the studyindexer to see if a user’s question is referencing a known assignment.  
   • Code for returning warnings if a user is effectively asking for direct assignment solutions.  
   • This is invoked from the course_guide_class in some places, so you can see how one might add additional logic.

4.7 supervisor_class.py  
   • The “Supervisor” agent that routes queries to the correct downstream agent (faq_agent, course_guide, or dismiss).  
   • It can also handle “complex queries” by first calling “_is_complex_query” (discovered via an LLM prompt), then “_break_down_query” to produce subquestions.  
   • For each subquestion, it decides which agent is best.  
   • Once all subquestions have results, it calls “generate_final_response” to produce a single combined answer.  

4.8 supervisor.py  
   • The node used by the StateGraph called “supervisor_node.”  
   • Orchestrates the workflow by checking if subquestions exist, if so, routes them to the correct agent, etc.  
   • After everything, it calls supervisor’s “generate_final_response” to piece together the final answer.

--------------------------------------------------------------------------------
5. “src/prompt” Directory
--------------------------------------------------------------------------------
5.1 prompts.py  
   • Contains the text templates used by the Supervisor agent to:  
       – Check if a query is “complex” (COMPLEX_QUERY_PROMPT).  
       – Decide which route to direct a single question (get_routing_prompt).  
       – Break down a complex query into subquestions (BREAKDOWN_QUERY_PROMPT).  
       – Finally synthesize subquestion answers (get_response_synthesis_prompt).  
   • These are standard text prompts for hooking into an LLM, supplemented with short instructions.

--------------------------------------------------------------------------------
6. “src/routes” Directory
--------------------------------------------------------------------------------

6.1 basic_routes.py  
   • Defines a variety of REST endpoints:  
       – “POST /{user_id}/session” creates a new chat session  
       – “GET /session/{session_id}” gets all session info (messages, user id, etc.)  
       – “GET /sessions” lists chat sessions for a user  
       – “PATCH /session/{session_id}” to patch session metadata (e.g. rename the session)  
       – “POST /report/{session_id}” to file a report about an AI message  
       – “GET /reports” to see all reported messages  
   • Also has “POST /message” to do a one-shot bare LLM call (through process_message in workflow_services).  
   • The route functions rely on the DB session from get_db.  

6.2 websocket_routes.py  
   • Provides the “/stream/chat/session/{session_id}/message” WebSocket.  
   • The client sends JSON with { message: “User’s text…” }.  
   • The server processes it (calls process_and_stream_message) and streams out chunks.  
   • This is how you get real-time AI chat behavior with partial tokens or chunk-based streaming.  

--------------------------------------------------------------------------------
7. “src/services” Directory
--------------------------------------------------------------------------------
7.1 basic_services.py  
   • Provides DB utilities to manipulate chat sessions, messages, and reports:  
       – create_new_session  
       – add_message_to_session  
       – list_sessions / list_sessions_with_counts  
       – delete_session  
       – report_message (where a user can report a bot’s message)  
       – apply_session_patch / apply_report_patch for handling JSONPatch-based updates.  
   • The main infrastructure for reading/writing from the ChatSession or Message tables is here.

7.2 websocket_services.py  
   • Manages the active WebSocket connections in a dictionary keyed by session_id, plus locks to avoid concurrency issues.  
   • connect(...) and disconnect(...) handle the handshake.  
   • process_and_stream_message(...) calls the workflow’s process_message_stream function, sending chunk responses as soon as they’re available.  
   • Also includes a global is_shutting_down variable to gracefully close all connections on server shutdown.

7.3 workflow_services.py  
   • Defines how the StateGraph is actually used in streaming mode:  
       – initialize_workflow(thread_id) loads or creates a new state machine with create_workflow.  
       – process_message(...) is a single-shot helper that calls LLM with ChatGoogleGenerativeAI.  
       – process_message_stream(...) is the method that steps through the workflow, yielding AI chunks.  
         It calls add_message_to_session once the AI message is fully formed.  
   • This is effectively the “bridge” between the user chat session, the agent workflow, and the final LLM logic.

--------------------------------------------------------------------------------
8. Putting It All Together
--------------------------------------------------------------------------------

• The StudyAI system is built with FastAPI plus a custom state machine (StateGraph from langgraph).  
• When you send a message (REST or WebSocket), the system checks for an existing conversation workflow or creates a new one.  
• The first node is check_question_type_node:
  1) If “Inappropriate” or “Generic,” it dismisses.  
  2) Otherwise, it goes to supervisor_node.  
• The “Supervisor” agent decides if the query is “complex,” and if so, breaks it into subquestions. Each subquestion is routed to either the “faq_agent” or “course_guide_agent.”  
   – The “faq_agent” calls the studyindexer “/faq/search” endpoint to retrieve relevant FAQ data.  
   – The “course_guide_agent” calls the “/course-selector/search” endpoint for relevant course matches, optionally “/course-content/search” for deeper content, or uses local mock data.  
• Each node appends relevant “findings” to the AgentState.  
• Once all subquestions have results, the “Supervisor” synthesizes them via a final LLM prompt, returning a single coherent answer.  
• The final text is stored in the DB as a bot message, then streamed back to the client.  
• The user can optionally “report” any bot message that is inappropriate or incorrect, stored in the “reported_responses” table.

In short, StudyAI is a multi-agent orchestration system that merges LLM capabilities (through Google’s Gemini / ChatGoogleGenerativeAI) with retrieval from an external “studyindexer” knowledge base. It uses a sophisticated workflow approach (langgraph) to interpret user queries, break them down into subquestions if needed, dispatch them to specialized agents, and unify the answers into one helpful response.
