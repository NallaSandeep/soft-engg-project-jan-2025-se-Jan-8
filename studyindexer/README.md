# StudyHub Platform

A comprehensive educational platform for course management, document processing, and AI-assisted learning.

## Project Structure

```plaintext
/
├── documentation/           # Comprehensive documentation
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_BACKEND_SETUP.md
│   ├── 02_FRONTEND_SETUP.md
│   ├── 03_STUDYINDEXER_SETUP.md
│   ├── 04_CONTRIBUTING.md
│   ├── 05_DEVELOPMENT_STATUS.md
│   ├── 06_API_REFERENCE.md
│   └── 07_SYSTEM_INTEGRATION.md
│
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

## Components

### 1. StudyHub Main Application
- Course management system
- User authentication
- Assignment handling
- Resource management

### 2. StudyIndexer Service
- Document processing
- Vector search
- Personal knowledge base
- Course-specific collections

### 3. StudyAI Service (Planned)
- AI-powered assistance
- Content recommendations
- Learning path optimization
- Personalized tutoring

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd studyhub-platform
```

2. Run the reorganization script (if needed):
```powershell
.\reorganize.ps1
```

3. Set up individual components:

```powershell
# Backend setup
cd studyhub/backend
.\setup.ps1

# Frontend setup
cd ../frontend
.\setup.ps1

# StudyIndexer setup
cd ../../studyindexer
.\setup.ps1
```

## Development

Each component can be developed independently:

### Backend
```powershell
cd studyhub/backend
python wsgi.py
```

### Frontend
```powershell
cd studyhub/frontend
npm start
```

### StudyIndexer
```powershell
cd studyindexer
.\start.ps1
```

## Documentation

Comprehensive documentation is available in the `/documentation` directory:

- Project Overview
- Setup Guides
- API Reference
- Development Status
- Integration Guide

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See `/documentation/04_CONTRIBUTING.md` for detailed guidelines.

## License

This project is licensed under [appropriate license]. See LICENSE file for details. 