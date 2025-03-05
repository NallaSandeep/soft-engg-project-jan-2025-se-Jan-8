# StudyHub Configuration Standards

This document defines the standardized configuration approach for all StudyHub applications.

## Hostname Standards

For consistency across all applications, we will use the following hostname standards:

| Usage | Value | Explanation |
|-------|-------|-------------|
| **Binding Services** | `0.0.0.0` | Use when a service needs to be accessible from other machines |
| **Local Connections** | `localhost` | Use when connecting to a service on the same machine |
| **Health Checks** | `localhost` | Use for health checks and internal service communication |

## Port Standards

The following ports are reserved for specific services:

| Service | Port | Notes |
|---------|------|-------|
| StudyHub Backend | 5100 | Flask API server |
| StudyHub Frontend | 3000 | React development server |
| StudyIndexer API | 8080 | FastAPI server |
| ChromaDB | 8000 | Vector database |
| Redis | 6379 | In-memory data store |

## Security Standards

For development environments, use these standard security values:

| Setting | Value | Notes |
|---------|-------|-------|
| API Key | `studyhub_dev_api_key_2024` | For service-to-service authentication |
| JWT Secret | `studyhub_development_jwt_secret_key_32chars` | For JWT token signing |
| JWT Algorithm | `HS256` | Standard JWT signing algorithm |
| JWT Expiration | `86400` (24 hours) | Token lifetime in seconds |

**IMPORTANT**: These values are for development only. Production environments must use different, secure values.

## Environment Files

Each application should have exactly ONE `.env` file for configuration and a corresponding `.env.example` file for documentation:

| Application | Config File | Example File |
|-------------|-------------|--------------|
| StudyHub Backend | `studyhub/backend/.env` | `studyhub/backend/.env.example` |
| StudyHub Frontend | `studyhub/frontend/.env` | `studyhub/frontend/.env.example` |
| StudyIndexer | `studyindexer/.env` | `studyindexer/.env.example` |

## Cross-Service Integration

Services should reference each other using environment variables:

| From | To | Environment Variable |
|------|----|--------------------|
| Backend → StudyIndexer | `INDEXER_SERVICE_URL=http://localhost:8080` | |
| Frontend → Backend | `REACT_APP_API_URL=http://localhost:5100/api/v1` | |
| Frontend → StudyIndexer | `REACT_APP_INDEXER_URL=http://localhost:8080` | |

## CORS Configuration

CORS settings should allow communication between services:

| Service | Allowed Origins |
|---------|----------------|
| Backend | `http://localhost:3000,http://127.0.0.1:3000` |
| StudyIndexer | `http://localhost:3000,http://localhost:5100` |

## File Storage Paths

Standardized paths for file storage:

| Purpose | Path |
|---------|------|
| Uploads | `./uploads` |
| Processed Files | `./data/processed` |
| Temporary Files | `./data/temp` |
| Logs | `./logs` |
| ChromaDB Data | `./data/chroma` |

## Logging Standards

Consistent logging configuration:

| Setting | Value |
|---------|-------|
| Log Level | `INFO` (development), `WARNING` (production) |
| Log Format | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` |

## Health Check Endpoints

Standard health check endpoints:

| Service | Endpoint |
|---------|----------|
| StudyIndexer FastAPI | `/health` |
| ChromaDB | `/api/v1/heartbeat` |
| Backend | `/api/v1/health` | 