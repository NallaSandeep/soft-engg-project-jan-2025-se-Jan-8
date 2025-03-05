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
├── studyhub/               # Main application
│   ├── backend/           # Flask backend service
│   │   ├── app/          # Application code
│   │   ├── scripts/      # Utility scripts
│   │   └── setup.ps1     # Backend setup
│   │
│   └── frontend/         # React frontend
│       ├── src/          # Source code
│       ├── public/       # Static assets
│       └── setup.ps1     # Frontend setup
│
├── studyindexer/          # Document processing service
│   ├── app/              # FastAPI application
│   ├── data/             # Data storage
│   │   ├── chroma/      # Vector database
│   │   ├── processed/   # Processed documents
│   │   └── uploads/     # Document uploads
│   ├── logs/            # Service logs
│   └── setup.ps1        # Service setup
│
└── studyai/              # Future AI service (planned)
```

## Quick Start Guide

### Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd studyhub-platform
   ```

2. **Backend Setup**:
   ```bash
   cd studyhub/backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python scripts/init_db.py
   flask run
   ```

3. **Frontend Setup**:
   ```bash
   cd studyhub/frontend
   npm install
   npm start
   ```

4. **StudyIndexer Setup**:
   ```bash
   # Needs WSL for Windows or Linux (Ubuntu)
   cd studyindexer
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage_services.py setup
   python manage_services.py start
   python manage_services.py status
   ```

## Development Environment

- **Prerequisites**:
  - Python 3.x
  - Node.js (v14 or higher)
  - npm (comes with Node.js)
  - Git
  - PostgreSQL (optional - SQLite is used by default in development)

## Key Features

- **Course Management**: Create and manage courses, materials, and assignments.
- **Document Processing**: Index and search documents using vector embeddings.
- **AI-Powered Learning**: Chat with an AI assistant for course-related queries.
- **Personal Knowledge Base**: Manage personal study notes and resources.

## Links to Submodule Documentation

- [StudyHub Documentation](studyhub/README.md)
- [StudyIndexer Documentation](studyindexer/README.md)
- [StudyAI Documentation](studyai/README.md)
