# StudyHub

A comprehensive study material management and indexing system that uses AI to help organize and search through study materials.

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

Please read [DEVELOPMENT_WORKFLOW.md](documentation/project/DEVELOPMENT_WORKFLOW.md) for details on our development process.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 