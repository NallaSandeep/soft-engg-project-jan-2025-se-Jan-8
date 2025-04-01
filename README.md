# StudyHub Platform

A comprehensive educational platform for course management, document processing, and AI-assisted learning.

## Project Overview

StudyHub is a SEEK-like learning management system that provides a comprehensive platform for academic course management and student learning. The platform enables:

- **Admins & TAs**: Create and manage courses, materials, and assignments
- **Students**: Access course materials, complete assignments, and track academic progress
- **AI-Powered Learning**: Chat with an AI assistant about courses, FAQs, and general queries
- **Personal Knowledge Base**: Students can create and reference their own study notes through the chat interface

## Project Structure

```plaintext
/
├── studyhub/             # Main application
│   ├── backend/          # Flask backend service
│   │   ├── app/          # Application code
│   │   ├── scripts/      # Utility scripts
│   │   └── setup.ps1     # Backend setup
│   │
│   └── frontend/         # React frontend
│       ├── src/          # Source code
│       ├── public/       # Static assets
│       └── setup.ps1     # Frontend setup
│
├── studyindexer/         # Document processing service
│   ├── app/              # FastAPI application
│   ├── data/             # Data storage
│   │   ├── chroma/       # Vector database
│   │   ├── processed/    # Processed documents
│   │   └── uploads/      # Document uploads
│   ├── logs/             # Service logs
│   └── setup.ps1         # Service setup
│
└── studyai/              # Future AI service (planned)
```

## Quick Start Guide

### Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/NallaSandeep/soft-engg-project-jan-2025-se-Jan-8.git
   ```

2. **Backend Setup**:
a. Change directory
   ```powershell
   cd .\studyhub\backend
   ```

b Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate     # Linux/macOS
   ```

c. Run the setup script:
   ```powershell
   .\setup.ps1
   ```
   This will:
   - Activate the virtual environment
   - Install all required dependencies
   - Initialize the database (if not already initialized)
   - Create necessary directories

d. Start the server:
   ```powershell
   .\start.ps1
   ```
   The API will be available at: http://localhost:5000

3. **Frontend Setup**:
a. Change directory
   ```powershell
   cd .\studyhub\frontend
   ```

b. Run the setup script:
   ```powershell
   .\setup.ps1
   ```
   This will:
   - Create required directories
   - Install dependencies
c. Start the development server
   - `npm start`: Start development server

d. Access the application:
   - Local: http://localhost:3000
   - Network: http://172.20.16.1:3000

4. **StudyIndexer Setup**: 
# Needs WSL for Windows or Linux (Ubuntu)
a. Change directory
   ```bash
   cd studyindexer

a. Run the setup script:
   ```bash
   ./setup.sh
   ```
   This will:
   - Create required directories
   - Install dependencies

b. Run the application:
```bash
   python manage_services.py setup
   ```
```bash
   python manage_services.py start
   ```
This will:
   - Starts ChromaDB
   - Starts FastAPI (This takes 2-3 mins)
   - Check status using below command

```bash
   python manage_services.py status
   ```
   - Keep checking status (for 2-3 mins)
   - Check logs if the issue persists even after 3 mins

```bash
   python manage_services.py restart
   ```
   - Restarts chroma db and FastAPI

4. **StudyAI Setup**: 
# Needs WSL for Windows or Linux (Ubuntu)
1. Change directory:
   ```bash
    cd studyai
   ```

2. Create a virtual environment:
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv/Scripts/activate
   ```

3. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Configure the `.env` file with your API keys (see API Key Setup section below)

5. Start the development server:
   ```bash
    python app.py
    # or
    uvicorn app:app --reload
   ```

## API Key Setup

### Google Gemini API

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a google studio account(use personal email id) if you don't have one
3. Generate an API key from the home page
4. Add the API key to your `.env` file:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### LangSmith API

1. Create an account at [LangSmith](https://smith.langchain.com/)
2. Navigate to the API Keys section in your account settings
3. Create a new API key
4. Add the API key to your `.env` file:

   ```
   LANGCHAIN_API_KEY=your_api_key_here
   LANGCHAIN_PROJECT=your_project_name
   LANGSMITH_TRACING_V2=true
   ```



## Development Environment

- **Prerequisites**:
  - Python 3.x
  - Node.js (v14 or higher)
  - npm (comes with Node.js)
  - Git
  - SQLite
  - ChromaDB

## Key Features

- **Course Management**: Create and manage courses, materials, and assignments.
- **Document Processing**: Index and search documents using vector embeddings.
- **AI-Powered Learning**: Chat with an AI assistant for course-related queries.
- **Personal Knowledge Base**: Manage personal study notes and resources.

## Links to Submodule Documentation

- [StudyHub Documentation](studyhub/README.md)
- [StudyIndexer Documentation](studyindexer/README.md)
- [StudyAI Documentation](studyai/README.md)
