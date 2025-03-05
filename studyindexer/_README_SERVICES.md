# StudyIndexer Service Manager

This document explains how to use the new service manager script to manage all StudyIndexer services from a single terminal.

## Prerequisites

Before using the service manager, make sure you have the following installed:

1. Python 3.8+ with pip
2. Redis server
3. Required Python packages (in a virtual environment)

### Setting Up a Virtual Environment in WSL

Since WSL Ubuntu has an externally managed Python environment, you must use a virtual environment:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install required packages
pip install chromadb celery fastapi uvicorn python-dotenv requests
```

## Environment Configuration

The service manager is fully configurable through environment variables. A template file `.env.template` is provided with all available configuration options.

### Setting Up Your Environment

1. Copy the template to create your own `.env` file:
   ```bash
   cp .env.template .env
   ```

2. Edit the `.env` file to customize your configuration:
   ```bash
   nano .env
   ```

### Key Configuration Categories

The environment variables are organized into several categories:

#### General Settings
- `HOST`: Default host for the FastAPI server (default: `0.0.0.0`)
- `PORT`: Default port for the FastAPI server (default: `8080`)
- `HEALTH_CHECK_TIMEOUT`: Default timeout for health checks in seconds (default: `10`)
- `DEFAULT_STARTUP_TIME`: Default startup time for services in seconds (default: `2`)
- `REQUIRED_PACKAGES`: List of required Python packages to check during setup
- `SERVICE_START_ORDER`: Order in which services are started (default: `["redis", "chromadb", "celery", "fastapi"]`)
- `SERVICE_STOP_ORDER`: Order in which services are stopped (default: reverse of start order)

#### Redis Settings
- `REDIS_HOST`: Redis server host (default: `localhost`)
- `REDIS_PORT`: Redis server port (default: `6379`)
- `REDIS_START_CMD`: Command to start Redis (default: `sudo service redis-server start`)
- `REDIS_STOP_CMD`: Command to stop Redis (default: `sudo service redis-server stop`)
- `REDIS_REQUIRED`: Whether Redis is required for the application (default: `true`)
- `REDIS_STARTUP_TIME`: Time to wait after starting Redis in seconds (default: `2`)

#### ChromaDB Settings
- `CHROMA_HOST`: ChromaDB host (default: `0.0.0.0` for binding, `localhost` for connecting)
- `CHROMA_PORT`: ChromaDB port (default: `8000`)
- `CHROMA_REQUIRED`: Whether ChromaDB is required (default: `true`)
- `CHROMA_STARTUP_TIME`: Time to wait after starting ChromaDB in seconds (default: `15`)
- `INIT_CHROMA_COLLECTION`: Whether to initialize ChromaDB collection on startup (default: `true`)
- `CHROMA_COLLECTION_NAME`: Name of the ChromaDB collection (default: `general`)
- `CHROMA_ALLOW_RESET`: Allow reset for ChromaDB (default: `true`)
- `CHROMA_TELEMETRY`: Enable telemetry for ChromaDB (default: `false`)

#### Celery and FastAPI Settings
- `CELERY_START_CMD`: Command to start Celery worker (default: `celery -A app.core.celery_app worker --loglevel=info`)
- `CELERY_REQUIRED`: Whether Celery is required (default: `true`)
- `CELERY_STARTUP_TIME`: Time to wait after starting Celery in seconds (default: `5`)
- `FASTAPI_REQUIRED`: Whether FastAPI is required (default: `true`)
- `FASTAPI_STARTUP_TIME`: Time to wait after starting FastAPI in seconds (default: `3`)

#### File Type Settings
- `SUPPORTED_FILE_TYPES`: JSON array of supported MIME types for file uploads

### JSON Format for Lists and Arrays

For environment variables that represent lists or arrays (like `REQUIRED_PACKAGES` or `SERVICE_START_ORDER`), use valid JSON format:

```
REQUIRED_PACKAGES=["chromadb", "celery", "uvicorn", "fastapi", "python-dotenv", "requests"]
SERVICE_START_ORDER=["redis", "chromadb", "celery", "fastapi"]
SUPPORTED_FILE_TYPES=["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/markdown"]
```

## Using the Service Manager

The service manager provides a unified interface to manage all StudyIndexer services:

```bash
python manage_services.py [action] [--service SERVICE_NAME]
```

### Available Actions

- `setup`: Check and install prerequisites
- `start`: Start all services or a specific service
- `stop`: Stop all services or a specific service
- `restart`: Restart all services or a specific service
- `status`: Check the health of all services or a specific service

### Examples

#### Setup the environment
```bash
python manage_services.py setup
```

#### Start all services
```bash
python manage_services.py start
```

#### Start a specific service
```bash
python manage_services.py start --service chromadb
```

#### Stop all services
```bash
python manage_services.py stop
```

#### Check the status of all services
```bash
python manage_services.py status
```

## Continuous Health Monitoring

A separate script is provided for continuous health monitoring:

```bash
python health_monitor.py [--interval SECONDS] [--format text|log]
```

### Examples

#### Monitor health every 30 seconds with text output
```bash
python health_monitor.py --interval 30
```

#### Monitor health with log output
```bash
python health_monitor.py --format log
```

#### Run in the background with logging to a file
```bash
nohup python health_monitor.py --format log > health_monitor.log 2>&1 &
```

## How It Works

The service manager:
1. Loads configuration from environment variables
2. Launches each service as a separate background process
3. Tracks process IDs for management
4. Captures output from each service
5. Provides graceful shutdown

You don't need separate WSL terminals because each service runs as a separate process managed by the script.

## Services Managed

The service manager handles the following services:

1. **Redis Server**: Message broker for Celery
2. **ChromaDB**: Vector database for document embeddings
3. **Celery Worker**: Background task processing
4. **FastAPI Server**: REST API for the StudyIndexer

## Customizing Services

You can customize how services are started, stopped, and checked by modifying the environment variables in your `.env` file. For example:

- Change the port ChromaDB runs on:
  ```
  CHROMA_PORT=8001
  ```

- Change the order services are started:
  ```
  SERVICE_START_ORDER=["redis", "celery", "chromadb", "fastapi"]
  ```

- Make a service optional:
  ```
  CELERY_REQUIRED=false
  ```

## Troubleshooting

### ChromaDB Issues

If you encounter issues with ChromaDB:

1. Make sure ChromaDB is installed in your virtual environment:
   ```bash
   source .venv/bin/activate
   pip install chromadb
   ```

2. Check if the port specified in your `.env` file is available:
   ```bash
   netstat -tuln | grep $(grep CHROMA_PORT .env | cut -d= -f2)
   ```

3. Manually start ChromaDB to see any error messages:
   ```bash
   python -m chromadb.server.app --host 0.0.0.0 --port $(grep CHROMA_PORT .env | cut -d= -f2)
   ```

4. Verify your environment variables:
   ```bash
   cat .env | grep CHROMA
   ```

### Celery Worker Issues

If the Celery worker fails to start:

1. Make sure Redis is running:
   ```bash
   redis-cli -h $(grep REDIS_HOST .env | cut -d= -f2) -p $(grep REDIS_PORT .env | cut -d= -f2) ping
   ```

2. Check the Celery configuration in `app/core/celery_app.py`

### FastAPI Server Issues

If the FastAPI server fails to start:

1. Make sure the port specified in your `.env` file is available:
   ```bash
   netstat -tuln | grep $(grep PORT .env | cut -d= -f2)
   ```

2. Check the server configuration in `main.py`

3. Verify your environment variables:
   ```bash
   cat .env | grep PORT
   ```

## Logs

Service logs are displayed in the terminal. For persistent logging, consider redirecting the output:

```bash
python manage_services.py start > studyindexer.log 2>&1 &
```

## Adding New Services

To add a new service to the manager, you would need to:

1. Add the service definition to the `SERVICES` dictionary in `manage_services.py`
2. Add appropriate environment variables to your `.env` file
3. Update the `SERVICE_START_ORDER` and `SERVICE_STOP_ORDER` variables to include the new service 