# StudyHub

A comprehensive study material management and indexing system that uses AI to help organize and search through study materials.

## Quick Start with GitHub Codespaces

1. Click the green "Code" button above
2. Select "Open with Codespaces"
3. Click "New codespace"

That's it! GitHub will automatically:
- Set up the development environment
- Install all dependencies
- Configure Docker
- Start all services

Your application will be available at:
- Frontend: https://[codespace-name]-3000.preview.app.github.dev
- Backend API: https://[codespace-name]-5000.preview.app.github.dev
- StudyIndexer API: https://[codespace-name]-8000.preview.app.github.dev

## Development in Codespaces

All services are running in Docker containers:
- `frontend`: React application
- `backend`: Flask API
- `studyindexer`: FastAPI service
- `chromadb`: Vector database
- `redis`: Cache and message broker

### Useful Commands

```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f

# Restart a service
docker compose restart [service-name]

# Rebuild and restart all services
docker compose up -d --build
```

## Project Structure

- `studyindexer/` - AI-powered document indexing and processing module
- `studyhub/` - Main application core
- `docker/` - Docker configuration and deployment files
- `documentation/` - Project documentation and guides

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js (for frontend)

## Quick Start

1. Clone the repository:
```bash
git clone [repository-url]
cd studyhub
```

2. Set up environment variables:
```bash
cp docker/.env.example docker/.env
# Edit .env file with your configurations
```

3. Start the services:
```bash
cd docker
docker compose up -d
```

## Development Setup

See [SETUP_GUIDE.md](documentation/project/SETUP_GUIDE.md) for detailed development setup instructions.

## Documentation

- [Architecture Overview](documentation/project/ARCHITECTURE.md)
- [Development Workflow](documentation/project/DEVELOPMENT_WORKFLOW.md)
- [API Documentation](documentation/api/)
- [Troubleshooting Guide](documentation/project/TROUBLESHOOTING.md)

## Contributing

1. Create a new branch
2. Make your changes
3. Submit a pull request

## Troubleshooting

If you encounter any issues:
1. Check the logs: `docker compose logs -f`
2. Rebuild services: `docker compose up -d --build`
3. Reset Codespace: Click "Stop Current Codespace" and create a new one

## License

This project is licensed under the MIT License - see the LICENSE file for details. 