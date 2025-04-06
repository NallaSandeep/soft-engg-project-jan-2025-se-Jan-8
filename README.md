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
├── studyai/              # Document processing service
│   ├── app.py            # FastAPI application
│   ├── src/             
│   │   ├── core/         # Core components (agents, workflow)
│   │   ├── models/       # Processed documents
│   │   └── modules/      # Agent modules
│   │   └── routes/       # API routes
│   │   └── services/     # Business logic
│   │   └── database.py   # Database connection
│   ├── config.py         # Configuration management
│   └── requirements.txt  # Python dependencies

```

## Quick Start Guide

### Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/NallaSandeep/soft-engg-project-jan-2025-se-Jan-8.git
   ```

2. **StudyIndexer Setup**: (Needs WSL for Windows or Linux (Ubuntu))

   a. Change directory
      ```bash
      cd studyindexer
      ```

   b Create and activate a virtual environment:
      ```powershell
      python -m venv .venv
      .\.venv\Scripts\activate  # Windows
      # or
      source .venv/bin/activate     # Linux/macOS

   c. Run the setup script:
      ```bash
      ./setup.sh
      ```
      This will:
      - Create required directories
      - Install dependencies

   d. Run the application:
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
      Use this when the data structure inside **ChromaDB** changes:
      ```bash
      python manage_services.py restart
      ```
      Use this for a faster restart (only restarts **FastAPI**):
      ```bash
      python manage_services.py quickstart
      ```
      To check if **StudyIndexer** is running:
      ```bash
      python manage_services.py status
      ```

   e. Reset ChromaDB
      - Open the Swagger Interface in your browser:
         [http://127.0.0.1:8081/docs](http://127.0.0.1:8081/docs)
      - Navigate to the `Development` section.
      - Locate the following endpoint:
         ```
         DELETE /api/v1/course-content/reset
         ```
      - Execute this endpoint to completely delete all data from ChromaDB.

      > ⚠️ **Note:** This step is only required when major changes occur (e.g., today). It is **not** necessary to run this every time.

   f. Start loading the course data
      - Once the **StudyIndexer** is running, proceed to the next step.
      - In the **PowerShell terminal**, navigate to `studyhub/backend` and run the following commands:
         ```powershell
         .\setup.ps1 
         (or)
         python .\scripts\init_db.py
         ```
         > **Note:** This process may take some time.  
         > It loads all the course files from `studyhub/backend/scripts/course` one by one into **StudyHub**, and also ingests them into the **StudyIndexer APIs**.

         Check the logs for any **Errors** — these need immediate attention.

   g. Load the FAQ Data
      - Add the 4 `*.jsonl` files located in `studyindexer/content/FAQ` **one by one** through the Swagger interface.
      - Navigate to: `FAQ -> Import JSON`
      - Use the following endpoint:
         ```
         POST /api/v1/faq/import
         ```
   h. Start All Other Services
   
      - Now that everything is set up, go ahead and start the rest of the services.

3. **Backend Setup**:

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

4. **Frontend Setup**: (Need Node and NPM installed)

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


5. **StudyAI Setup**: 

   a. Change directory:
      ```bash
      cd studyai
      ```

   b. Create a virtual environment:
      ```bash
      python -m venv venv
      source venv/bin/activate  # On Windows: venv/Scripts/activate
      ```

   c. Install dependencies:
      ```bash
      pip install -r requirements.txt
      ```

   d. Set up environment variables:
      ```bash
      cp .env.example .env
      ```

   e. Configure the `.env` file with your API keys (see API Key Setup section below)

   f. Start the development server:
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
