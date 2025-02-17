Planned But Not Developed Features

1. Key Goals & Feature Breakdown
1.1 Open-Ended Chat with Enhanced Controls
ChatGPT-style interface for Students (with potential to expand to TAs/Admin):
Thread-based conversations (with an option to archive, delete, favorite, rate).
We want a system that says, “As a student, I can open or reopen a chat thread and see the entire context.”
1.2 Vector Databases for RAG
We intend to have three sets of vector indexes:
Course-based (public to the enrolled students).
Personal knowledge base (private to an individual student).
General FAQ (Institute-level or universal).
The chat logic (a.k.a. Supervisor or Agentic approach) decides which of these indexes to tap into.
If a user references a specific course (“@week4” or “@lecture2.1”), we incorporate that index.
If the user’s personal notes might be relevant, we search that as well.
If it’s a general question (like “When do midterm exams happen?”), we query the general FAQ index.
1.3 IntegrityAgent
We want a step in the pipeline that detects if the question is referencing a graded assignment.
If it is, we replace direct solution with “conceptual hints,” possibly randomizing numeric values or focusing on related concepts.
This agent is integrated at the Supervisor level to catch offending queries.
1.4 Document Indexer
A background job (Celery or RQ-based) that receives new or updated documents from StudyHub and transforms them into embeddings, stored in the relevant vector DB:
Course doc → Goes to that course’s sub-collection or vector space.
Personal doc → Goes to that user’s personal KB.
General doc → Goes to the general FAQ collection.
1.5 Full “Agentic” AI Subsystem
Instead of a single monolithic approach, we have a “Supervisor” or “Orchestrator” node that:
Classifies the query (which course or knowledge base?).
Checks integrity constraints.
Calls the RAG pipeline (with the relevant vector store or stores).
Possibly merges results from multiple indexes.
Produces a final answer and logs conversation info.
2. Proposed Flow for Chat & Indexing
2.1 Chat: High-Level Steps
StudyHub → The front end has a React page for chat. The user has a list of previous threads (like email threads). They open one or create a new one.
User Submits Query → We gather context: user_id, role=“Student,” (and from the DB: user’s enrolled courses, personal KB presence, etc.).
APICall → (POST /api/chat on the AI subsystem or via the StudyHub gateway) with that context info.
Supervisor / Orchestration
(a) Classification: Determine if the question references a particular course or personal notes (detect “@lecture2.1,” “@week4,” or key phrases).
(b) Check Integrity: If a direct graded assignment is found, shift the prompt or short-circuit the answer to hints only.
(c) RAG: Query the relevant vector DB(s). If multiple are relevant (say, “statistics” and “linear algebra”), gather top docs from both.
(d) Combine + Summarize: Possibly unify partial results.
(e) Return the final text to the user.
Chat Storage → Save the entire user message + AI response in conversation logs (which we might store in the StudyHub DB to keep consistent with user management).
2.2 Document Indexer (Celery)
Trigger: TAs or Students upload a doc in StudyHub. That doc is flagged with “included_in_ai = true” and associated metadata (course_id=..., user_id=..., doc_type=“pdf,” etc.).
StudyHub → calls the DocumentIndexer API or enqueues a job with Celery, specifying doc_id.
Indexer → chunk+embed the doc:
Possibly using a library like langchain.text_splitter.RecursiveCharacterTextSplitter.
Use an embedding model, e.g. sentence-transformers/all-MiniLM-L6-v2.
Insert embeddings into Chroma or FAISS with metadata: { doc_id, course_id, user_id, etc. }.
Vector DB is updated. Now, queries that match this doc’s content will be found during RAG.
3. Data & Architecture Brainstorming
3.1 Where to Store Chat?
If we want a single, consistent user-experience and single sign-on, it’s probably best if StudyHub has a “chat_messages” or “conversations” table:
conversation_id, user_id, message_role (assistant/user), content, created_at, etc.
This ensures each conversation can be archived, deleted, rated, etc.
3.2 The AI Chat API & Database
The AI Chat logic (LangChain or other) might not store conversation logs internally. Instead it can request the conversation context from StudyHub if needed.
Alternatively, we do store ephemeral partial states if we want to let the LLM handle the entire chain. But typically, storing “source-of-truth” in StudyHub is simpler (the AI can fetch previous messages from an endpoint).
3.3 Multiple Agents / “Supervisor”
The top-level “Supervisor” agent might do classification:
Which vector DB or sub-collection: “course_{id}, user_{id}, general_faq.”
Academic Integrity: If this is a direct solution request, pass it to “IntegrityAgent.”
Then pass the sanitized or partial question to the “RAGAgent.”
Each agent is a node in a chain. After RAGAgent returns a proposed answer, we might pass it to a final “Response QA” node that ensures no direct solutions.
3.4 Example: Student Asks a “Pointers” Question
Student is enrolled in “C++ Basics” (course_id=14). They say “@week2: Pointers are confusing. How do I solve assignment 2’s pointer question?”
System sees references: “@week2,” “assignment 2,” “pointers.”
Supervisor:
Realizes it’s course 14, calls the “IntegrityAgent” to check if assignment2 is a graded one. If so, we must withhold direct solutions.
The question is sanitized to “Explain the concept of pointers” or “What are typical pointer manipulations?”
Then we do RAG on course_14 index plus the student’s personal KB if they have any pointer notes.
The retrieved chunks + LLM produce an explanation.
Final text is returned.
4. Implementation Details
4.1 Tech Stacks
DocumentIndexer

Celery (with Redis or RabbitMQ) as the message broker.
A Python function index_doc(doc_id) that queries StudyHub DB for the doc content, chunk+embed, store in FAISS/Chroma.
Typically no direct “HTTP API” in Celery. We do: celery_app.send_task("index_doc", args=[doc_id]). If you want a small REST wrapper, you can build it, but it’s not typical to have a Celery worker itself exposing HTTP.
AI Chat

Possibly a separate Flask/FastAPI app running on :5001.
POST /api/chat: input: { user_id, message, conversation_id, subscribed_courses, etc. }
Output: { response_text, some metadata }
Inside, we have the “Supervisor” chain with IntegrityAgent, RAGAgent, etc.
Vector DB

We can store course-based chunks in a single index but with “metadata={ course_id:14 }.”
For personal docs: “metadata={ user_id:123 }.”
For general: “metadata={ scope:'general_faq' }.”
When we do a similarity search, we post-filter by the user’s course or personal doc IDs.
4.2 Chat UI with Controls
Archive: We add a field conversation.status=‘archived.’ The user can hide it from main view.
Delete: Soft delete or fully remove from DB.
Favorite: conversation.is_favorite=Boolean.
Rate: We store a rating: “GOOD/BAD/RETRY.” Potentially triggers feedback loop?
Open/Reopen: The front-end just changes the conversation’s status from archived/closed to active.
4.3 IntegrityAgent Implementation
We maintain a small sub-DB table of “graded_assignments” with keywords or partial solutions for identification.
If the user’s question hits a certain similarity threshold to a known assignment question, or references “@GA2.3,” we do partial answer logic.
Alternatively, we detect direct code block requests or numeric solution requests.
4.4 Merging Multiple Vector Indices
Because we have separate sub-collections for “course_{id}, user_{id}, general,” we might do queries across them if the question seems broad.
Or we do a step that merges top-k from each relevant index.
The RAG pipeline merges them before passing to the LLM for final answer.
5. Next Steps for the Development
Implement the DocumentIndexer as a Celery worker.

Add triggers in StudyHub: whenever a doc is marked “included_in_ai,” we call send_task("index_doc", doc_id=123).
The worker chunk+embeds, saving to vector DB.
Set Up the AI Chat API with a simple “Supervisor” logic.

Write supervisor.py that does classification + integrity checks + RAG calls.
Possibly unify with your existing “Chat endpoint” stub, so the front end just calls it with the conversation context.
Store Chat Threads in the main StudyHub database.

Provide front-end pages for archive, favorite, rating, etc.
Refine the IntegrityAgent

Keep a minimal detection approach for now (like “if user references a known assignment code, we flip to hints-only”).
Figure Out the Approach for Multi-Vector

We do “one big index with metadata.” Or multiple sub-collections. For the MVP, many teams do “one big index + metadata.” Post-filter is easy.
If it’s easier for you to have separate indices, do so but handle searching all relevant indices in code.
6. Additional Brainstorming Points
Where to store chunk text?
Typically in the vector DB metadata or a sidecar relational DB table. Some vector DBs like Chroma store chunk text internally with metadata.
Which retrieval algorithm?
Basic kNN with L2 or cosine similarity. For FAISS, IndexFlatIP or IndexFlatL2 is straightforward.
Do we need advanced orchestration like “LangChain Router chains?”
Possibly yes if we have many specialized sub-agents. But a simpler if-else Supervisor can do for now.
LLM usage
If cost is a factor, we might start with OpenAI GPT-3.5 or a local model (sentence-transformers for generation?). We can always swap.
Storing conversation logs
Potentially large. We can store only user messages + AI outputs, or we can do advanced summarization. That’s a future step.
Conclusion
This set of next features establishes the core advanced functionality:

A stable chat interface with archiving, rating, and so on.
Agentic approach to deciding which indexes to use, how to respond with partial/hint-based answers for graded questions, and how to handle personal or general data.
Document Indexing so new or updated docs get seamlessly integrated into the RAG pipeline.
In practical terms, you’ll probably:

Start by coding the DocumentIndexer Celery pipeline.
Implement or finalize the AI Chat (with Supervisor + IntegrityAgent + RAG).
Provide the front-end “Chat” page with the CRUD (archive, favorite, etc.).
Then unify it all into an end-to-end MVP.
That’s it for a high-level dev plan. Once you finalize these, you can chunk the tasks into JIRA tickets:

“Implement Celery-based indexer for course docs”
“Add personal KB indexing for student docs”
“Set up AI Chat Supervisor with references to multiple vector DB sets”
“IntegrityAgent partial solution logic”
“Frontend Chat: archive/fav/rate UI.”
This approach ensures clarity on how your multiple vector indexes, agentic pipeline, and conversation storage all come together to produce the next iteration of features.