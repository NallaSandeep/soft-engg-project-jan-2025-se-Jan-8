StudyHub Academic Platform
Vision:
A centralized environment for course content delivery, student engagement, and AI-enhanced learning. The system has three distinct modules:

StudyHub (Core Platform)
StudyAI (AI Subsystem)
StudyIndexer (Vector Search & Indexing)
We keep them separate to ensure modular development (and easier collaboration), yet integrated enough to provide a smooth end-user experience.

<br/>
1. Users & Their Roles
1.1 Primary Users
Students

Access assigned courses, view lectures, attempt assignments, and chat with the AI (for clarifications, hints, or resources).
Key interactions: check grades, track progress, upload personal study materials (private knowledge base), ask questions in real-time chat.
1.2 Secondary Users
Teaching Assistants (TAs)

Manage the day-to-day aspects of each course: uploading lectures, notes, PDFs.
Configure which resources get indexed for AI retrieval (i.e., “included_in_ai: true/false”).
Monitor AI suggestions, especially for academic integrity (no direct solutions).
1.3 Tertiary Users
Admin

Full administrative privileges across the entire system: user/role creation, advanced analytics, global settings.
Potentially configure global “AI settings” or “policies.”
Software Development Team

Maintains the application’s back end (Flask, database, indexing pipeline) and front end (React).
Ensures robust APIs, LLM integrations, performance metrics, bug fixes.
<br/>
2. User Stories
Below are the main user stories aligned with our project scope. We follow the As a [user], I want [action], so that [benefit] format.

2.1 Student User Stories
Dashboard & Course Management

“As a student, I want to see all my enrolled courses and weekly resources in a single dashboard, so that I can easily organize my study schedule.”

AI Chat & Resource Tips

“As a student, I want to ask questions about course concepts in a chat interface, so that I can clarify doubts quickly and improve my understanding.”

Academic Integrity Nudges

“As a student, I want the AI to provide ‘nudges’ or hints instead of direct solutions for graded assignments, so that I learn concepts without violating academic integrity.”

Personal Study Material

“As a student, I want to upload my own notes/PDFs and have them included in my personal knowledge base, so that the AI can reference my custom material too.”

Progress Tracking

“As a student, I want to track my course progress (assignments done, quizzes, lecture views) in real time, so that I can plan and not fall behind.”

Bookmark Important Insights

“As a student, I want to bookmark or save AI recommendations or references, so that I can revisit key explanations later.”

<br/>
2.2 Teaching Assistant User Stories
Course Content Management

“As a TA, I want to create/edit course modules (lectures, reading materials) and tag them for AI indexing, so that students can access structured content and the AI can reference it.”

AI Policy Configuration

“As a TA, I want to configure the AI scope (e.g., if solutions to certain assignments are restricted), so that we comply with academic integrity guidelines.”

Analytics & FAQ

“As a TA, I want to see which questions are frequently asked, so that I can improve course materials or highlight tricky concepts in live sessions.”

Resource Upload

“As a TA, I want to upload PDF transcripts or lecture notes, so that the system can chunk/index them for easier retrieval by students.”

<br/>
2.3 Admin User Stories
Global Administration

“As an Admin, I want to manage user roles (create TAs, block certain accounts), so that the platform remains organized and secure.”

Advanced Analytics

“As an Admin, I want to see overall usage stats (AI queries, peak usage times, etc.), so that I can allocate resources or intervene if usage spikes.”

<br/>
2.4 Software Developer User Stories
Knowledge Base & Vector Index

“As a developer, I want to maintain an efficient vector store and chunking mechanism, so that the AI can provide accurate and context-aware answers.”

System Monitoring

“As a developer, I want to collect performance metrics (API latency, memory usage) to ensure the system handles concurrent loads gracefully.”

Academic Integrity

“As a developer, I want to implement the IntegrityAgent with partial solutions or numeric randomization for direct queries, so that we follow the no-direct-answers policy.”

<br/>
3. System Architecture & Modules
Here is an overview of our final design—no “maybe or if” placeholders; all decisions are pinned down for MVP.

3.1 Module Layout
pgsql
Copy
Edit
+------------------------------+
|          StudyHub            |  (Flask + React + Postgres)
|  (Portal: user mgmt,        |
|   courses, basic features)   |
+--------------+---------------+
               | (APIs)
               v
+------------------------------------+
|           StudyAI                  |  (Flask or FastAPI + LLM calls)
|   (Chat interface logic, RAG)      |
|   - Supervisor                     |
|   - RAGAgent, IntegrityAgent, etc. |
+--------------+----------------------+
               | (Indexes)
               v
+------------------------------+
|        StudyIndexer          | (Celery or RQ)
|  (Chunking, embedding, job   |
|   queue for new docs)        |
+--------------+---------------+
               | (Vector store)
               v
+------------------------------+
|         VectorDatabase       | (ChromaDB local store)
|   Single index with metadata |
+------------------------------+
StudyHub

Written in Flask for the backend (REST) + React for the front end.
Houses user login, roles, course CRUD, assignment management.
On doc upload (PDF or text), calls StudyIndexer to embed them.
StudyAI

A separate service or sub-application that runs the multi-agent approach.
Exposes an endpoint like /api/chat, taking queries and returning an answer.
Supervisor (the orchestrator) calls RAGAgent, IntegrityAgent, etc.
The RAGAgent fetches relevant chunks from VectorDatabase by course_id or user_id metadata.
StudyIndexer

Takes new or updated docs (both from TAs and from students for personal knowledge bases).
Splits text into chunks (~1000 tokens) using langchain.text_splitter or similar.
Embeds each chunk with a chosen model (currently sentence-transformers/all-MiniLM-L6-v2).
Saves embeddings + metadata to a single ChromaDB index (we store doc/course_id in a side dictionary or DB table for filtering).
VectorDatabase

Local ChromaDB index with a sidecar metadata map.
Single index approach: we do a post-filter on course_id or user_id to ensure only relevant chunks are used.
Rebuilding index or marking deleted IDs if doc changes drastically.
<br/>
4. Development Workflow & Hosting
4.1 GitHub Branches
main branch: stable code.
feature/* branches: new features or bug fixes.
Merged via Pull Request after code review.
Some developers prefer personal michael-beta branches for POC.
4.2 Technology Versions
Python 3.10+
Flask 2.x
PostgreSQL 14+
React 18+ with React Router 6
ChromaDB-cpu or ChromaDB-gpu (for local vector store)
4.3 Hosting (for MVP)
All on a single Ubuntu server (no Docker to keep it simpler for now).
StudyHub (Flask) runs on Gunicorn at port 5000, behind Nginx.
Frontend served by Nginx at / route.
StudyAI can run on port 5001, also behind Nginx.
StudyIndexer (Celery worker) is run as a background systemd service.
VectorDatabase stored in e.g. /var/lib/studybot/ChromaDB_index/.
<br/>
5. Current Development & Planned Features
5.1 Current State (MVP)
User Management: Admin can create TAs, TAs can create Students. Basic sign-in.
Courses & Basic Upload: TAs can upload PDFs or text for each course. The system stores them in Postgres, but not yet chunked/embedded.
Chat Endpoint: A sample AI endpoint exists but is not integrated with the vector store. Just a stub.
CI/CD: Basic script that restarts Gunicorn & Nginx on each push to main.
5.2 Next Steps
StudyIndexer: connect Celery to automatically chunk+embed newly uploaded docs, store them in ChromaDB with metadata.
StudyAI: finalize Supervisor → RAG pipeline → IntegrityAgent flow, plus the reference parsing (@Week2, etc.).
Integration: let StudyHub call /api/chat on StudyAI with user data (like course_id, user_id) so we can filter or do post-check in RAG.
Academic Integrity: ensure that queries referencing a graded assignment get either numeric randomization or conceptual hints from the AI rather than direct solutions.
<br/>
6. Rationale & Additional Notes
We choose a single index in ChromaDB approach (phase 1), storing doc/course/user IDs in a parallel structure or small metadata DB. Then we do post-filtering by user subscription or doc ownership.
For real-time doc updates, we do a full re-embed if the doc changes significantly. Partial re-index can come in phase 2.
We use Python-based chunking and embedding in StudyIndexer (wired with Celery + a simple Redis broker).
We do not rely on the LLM’s “global knowledge” for direct solutions; we keep everything Retrieval-Augmented to ensure we rely on the relevant chunk data. This fosters academic integrity and ensures consistent “no direct solutions to graded questions.”
<br/>
7. Conclusion & Path Forward
With the above plan:

Milestone 1: We finalize user identification, user stories (including academic integrity for TAs and students), and the high-level architecture.
Milestone 2: We implement the basic portal with login, course management, and minimal chat flow (without advanced RAG).
Milestone 3: Integrate StudyIndexer + StudyAI for real retrieval-augmented chat.
Milestone 4: Refine academic integrity logic, implement partial re-index or advanced analytics.
This structured approach ensures that each milestone builds on the previous. By the end, StudyHub will be a robust platform enabling interactive course content, personal knowledge bases, and AI guidance—while safeguarding academic standards.

How to Present This Milestone (in Confluence or Another Tool)
Introduction & Purpose: Summarize the project’s aim (AI-driven academic portal).
User Identification: List Primary (Students), Secondary (TAs), Tertiary (Admins/dev).
User Stories: Present them scenario by scenario (like in the final doc above).
System Architecture: Show a block diagram or bullet points of the 3 modules and how they tie together.
Current Development: Outline what’s done in MVP form (basic login, course creation, stub chat).
Planned: Summarize the next steps for indexing, AI synergy, integrity checks.
You can design it with nice headings, bullet points, and a few scenario-based visuals (like “User asks question about Lecture 2…”). That fosters clarity and meets the academic requirement of “Identify User Requirements” (i.e., who the users are, their roles, what they want to do, and the overall planned architecture).

End of Document