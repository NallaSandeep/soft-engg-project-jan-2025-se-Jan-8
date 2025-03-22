# StudyHub Backend

## Overview

Backend service for the StudyHub platform, providing user authentication, data management, and API endpoints for the frontend application.

## Prerequisites

- Python 3.x
- PostgreSQL
- Redis (for Celery)

## Project Structure

```plaintext
backend/
├── app/              # Main application code
├── migrations/       # Database migrations
├── tests/           # Test files
├── .env             # Environment configuration
├── setup.ps1        # Setup script
└── start.ps1        # Server startup script
```

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   # or
   source .venv/bin/activate     # Linux/macOS
   ```

2. Run the setup script:
   ```bash
   .\setup.ps1
   ```
   This will:
   - Activate the virtual environment
   - Install all required dependencies
   - Initialize the database (if not already initialized)
   - Create necessary directories

3. Start the server:
   ```bash
   .\start.ps1
   ```
   The API will be available at: http://localhost:5000

## Dependencies

Key dependencies include:
- Flask 3.1.0
- Flask-CORS 5.0.0
- Flask-JWT-Extended 4.7.1
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.37
- Redis 5.0.1
- Celery 5.3.6
- Python-dotenv 1.0.1

Development dependencies:
- pytest
- pytest-flask
- black
- flake8

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8
```

## Troubleshooting

1. **Database Issues**
   - Ensure PostgreSQL is running
   - Check database connection settings in `.env`
   - For fresh setup, delete existing database if you want to reinitialize

2. **Redis/Celery Issues**
   - Verify Redis is running
   - Check Redis connection settings in `.env`

3. **Port Conflicts**
   - Default port is 5000
   - Can be modified in `.env` file

## Environment Variables

Create a `.env` file with the following variables:
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=...
```

## API Documentation

### Authentication

- POST `/api/auth/login`: User login
- POST `/api/auth/register`: User registration
- POST `/api/auth/refresh`: Refresh access token

### Courses

- GET `/api/courses`: List courses
- POST `/api/courses`: Create course
- GET `/api/courses/{id}`: Get course details
- PUT `/api/courses/{id}`: Update course
- DELETE `/api/courses/{id}`: Delete course

### Assignments

- GET `/api/assignments`: List assignments
- POST `/api/assignments`: Create assignment
- GET `/api/assignments/{id}`: Get assignment details
- PUT `/api/assignments/{id}`: Update assignment
- DELETE `/api/assignments/{id}`: Delete assignment

## Development Guide

### Running Tests

```bash
pytest
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes

### Database Migrations

```bash
flask db migrate -m "Migration message"
flask db upgrade
```

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   - Check database URL in `.env`
   - Verify database service is running
   - Check permissions

2. **Authentication Errors**
   - Verify JWT secret key
   - Check token expiration
   - Validate request headers

3. **API Errors**
   - Check request format
   - Verify required fields
   - Review error logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request