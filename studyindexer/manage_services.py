#!/usr/bin/env python3
"""
StudyIndexer Service Manager
----------------------------
A comprehensive script to manage all StudyIndexer services.
"""
import os
import sys
import time
import signal
import argparse
import subprocess
import requests
import logging
import re
import json
import platform
from pathlib import Path
from dotenv import load_dotenv
import socket

# Configure logging
Path("logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "service-manager.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("service-manager")

# Load environment variables
def load_env_files():
    """Load environment variables from .env files"""
    # Load main .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        logger.info(f"Loading environment from {env_file}")
        load_dotenv(env_file)
    else:
        logger.warning(f"No .env file found at {env_file}")
        
    # Return a dict with all environment variables
    return dict(os.environ)

# Get environment variables with defaults
def get_env(key, default=None):
    """Get environment variable with default value"""
    return os.environ.get(key, default)

# Get environment variables as int with defaults
def get_env_int(key, default=None):
    """Get environment variable as integer with default value"""
    value = get_env(key, default)
    try:
        return int(value) if value is not None else None
    except ValueError:
        logger.warning(f"Environment variable {key} is not a valid integer: {value}. Using default: {default}")
        return int(default) if default is not None else None

# Get environment variables as list with defaults
def get_env_list(key, default=None, delimiter=','):
    """Get environment variable as list with default value"""
    value = get_env(key)
    if value is None:
        return default if default is not None else []
    try:
        # Try to parse as JSON first
        return json.loads(value)
    except json.JSONDecodeError:
        # Fall back to splitting by delimiter
        return [item.strip() for item in value.split(delimiter) if item.strip()]

# Load environment variables
ENV = load_env_files()

# Check if a port is in use
def is_port_in_use(port, host='127.0.0.1'):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

# Service definitions with environment variable support
SERVICES = {
    "chromadb": {
        "name": "ChromaDB",
        "start_cmd": f"chroma run --host 127.0.0.1 --port {get_env('CHROMA_PORT', '8000')} --path {get_env('CHROMA_PERSIST_DIR', './data/chroma')}",
        "health_url": f"http://127.0.0.1:{get_env('CHROMA_PORT', '8000')}{get_env('CHROMA_HEALTH_ENDPOINT', '/api/v2/heartbeat')}",
        "health_check": lambda: requests.get(f"http://127.0.0.1:{get_env('CHROMA_PORT', '8000')}{get_env('CHROMA_HEALTH_ENDPOINT', '/api/v2/heartbeat')}", timeout=get_env_int("HEALTH_CHECK_TIMEOUT", 10)).status_code == 200,
        "required": get_env("CHROMA_REQUIRED", "true").lower() == "true",
        "startup_time": get_env_int("CHROMA_STARTUP_TIME", 15)
    },
    "fastapi": {
        "name": "FastAPI Server",
        "start_cmd": f"uvicorn app:app --host 127.0.0.1 --port {get_env('PORT', '8081')} {get_env('DEBUG', 'false').lower() == 'true' and '--reload' or ''}",
        "health_url": f"http://127.0.0.1:{get_env('PORT', '8081')}{get_env('FASTAPI_HEALTH_ENDPOINT', '/api/health')}",
        "health_check": lambda: requests.get(f"http://127.0.0.1:{get_env('PORT', '8081')}{get_env('FASTAPI_HEALTH_ENDPOINT', '/api/health')}", timeout=get_env_int("HEALTH_CHECK_TIMEOUT", 10)).status_code == 200,
        "required": get_env("FASTAPI_REQUIRED", "true").lower() == "true",
        "startup_time": get_env_int("FASTAPI_STARTUP_TIME", 15)
    }
}

# Check prerequisites
def check_prerequisites():
    """Check if all prerequisites are installed"""
    logger.info("Checking prerequisites...")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        import chromadb
        import sentence_transformers
        import langchain
        logger.info("All required Python packages are installed")
    except ImportError as e:
        logger.error(f"Missing Python package: {e}")
        logger.error("Please install all required packages: pip install -r requirements.txt")
        return False
    
    # Check ChromaDB
    try:
        import chromadb
        logger.info(f"ChromaDB is installed: {chromadb.__version__}")
    except (ImportError, AttributeError):
        logger.warning("ChromaDB not installed or version not found")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.warning("Not running in a virtual environment. It's recommended to use a virtual environment.")
    
    # Check if directories exist
    data_dir = Path(get_env("DATA_DIR", "./data"))
    if not data_dir.exists():
        logger.info(f"Creating data directory: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
    
    uploads_dir = Path(get_env("UPLOADS_DIR", "./uploads"))
    if not uploads_dir.exists():
        logger.info(f"Creating uploads directory: {uploads_dir}")
        uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure logs directory exists with absolute path
    logs_dir = Path(os.path.abspath(get_env("LOG_DIR", "./logs")))
    if not logs_dir.exists():
        logger.info(f"Creating logs directory: {logs_dir}")
        logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create required log files if they don't exist
    required_logs = ["api.log", "info.log", "error.log"]  # Removed background.log
    for log_file in required_logs:
        log_path = logs_dir / log_file
        try:
            if not log_path.exists():
                logger.info(f"Creating empty log file: {log_path}")
                # Use open instead of touch for better compatibility
                with open(log_path, 'a'):
                    pass
        except Exception as e:
            logger.warning(f"Could not create log file {log_path}: {str(e)}")
            # Continue anyway, the logging system will try to create it when needed
    
    # All prerequisites satisfied
    logger.info("All prerequisites are satisfied")
    return True

# Initialize ChromaDB collection
def init_chroma_collection():
    """Initialize ChromaDB collection"""
    logger.info("Initializing ChromaDB collection...")
    
    # First, make sure ChromaDB service is running
    if not is_service_running("chromadb"):
        logger.warning("ChromaDB service is not running. Starting it now...")
        if not start_service("chromadb"):
            logger.error("Failed to start ChromaDB service. Cannot initialize collection.")
            return False
        
        # Give ChromaDB some time to fully initialize
        logger.info("Waiting for ChromaDB to fully initialize...")
        time.sleep(5)
    
    try:
        # Import here to avoid circular imports
        from app.services.chroma import ChromaService
        
        # Initialize ChromaDB service
        chroma_service = ChromaService()
        
        # Add a delay to ensure ChromaDB is fully ready
        time.sleep(2)
        
        # Get or create collection using the synchronous method
        try:
            collection = chroma_service.get_or_create_collection_sync("documents")
            logger.info(f"ChromaDB collection initialized: {collection.name}")
            logger.info(f"Collection count: {collection.count()}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return False
            
    except FileNotFoundError as e:
        # Check if it's specifically the background.log file
        if "background.log" in str(e):
            logger.warning(f"Ignoring missing background.log file: {str(e)}")
            # Try again without relying on the background logger
            try:
                from app.services.chroma import ChromaService
                chroma_service = ChromaService()
                collection = chroma_service.get_or_create_collection_sync("documents")
                logger.info(f"ChromaDB collection initialized: {collection.name}")
                return True
            except Exception as retry_error:
                logger.error(f"Failed to initialize ChromaDB collection after retry: {retry_error}")
                return False
        else:
            # Some other file not found error
            logger.error(f"Log file not found: {str(e)}")
            logger.info("Attempting to create missing log directories and files...")
            
            # Ensure logs directory exists with absolute path
            logs_dir = Path(os.path.abspath(get_env("LOG_DIR", "./logs")))
            if not logs_dir.exists():
                logger.info(f"Creating logs directory: {logs_dir}")
                logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Try again after creating log directories
            try:
                from app.services.chroma import ChromaService
                chroma_service = ChromaService()
                collection = chroma_service.get_or_create_collection_sync("documents")
                logger.info(f"ChromaDB collection initialized: {collection.name}")
                return True
            except Exception as retry_error:
                logger.error(f"Failed to initialize ChromaDB collection after retry: {retry_error}")
                return False
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB collection: {e}")
        return False

# Check if a service is running
def is_service_running(service_name):
    """Check if a service is running"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    
    try:
        response = requests.get(service["health_url"], timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Start a service
def start_service(service_name):
    """Start a specific service"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    
    if not service.get("required", True):
        logger.info(f"Skipping {service['name']} (not required)")
        return True
    
    logger.info(f"Starting {service['name']}...")
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Check if the service is already running
    if check_service_health(service_name):
        logger.info(f"{service['name']} is already running")
        return True
    
    # Check if port is in use
    port = int(get_env('CHROMA_PORT', '8000')) if service_name == "chromadb" else int(get_env('PORT', '8081'))
    if is_port_in_use(port):
        logger.error(f"Port {port} is already in use. Cannot start {service['name']}")
        return False
    
    # Start the service
    try:
        if platform.system() == "Windows":
            # Windows-specific start command
            cmd = f"start /B {service['start_cmd']} > logs\\{service_name}.log 2>&1"
            subprocess.Popen(cmd, shell=True)
        else:
            # Unix-specific start command
            cmd = f"nohup {service['start_cmd']} > logs/{service_name}.log 2>&1 &"
            subprocess.Popen(cmd, shell=True)
        
        logger.info(f"{service['name']} started")
        
        # Wait for the service to start
        startup_time = service.get("startup_time", 5)
        logger.info(f"Waiting {startup_time} seconds for {service['name']} to start...")
        time.sleep(startup_time)
        
        # Check if the service is healthy
        logger.info(f"Checking health of {service['name']}...")
        if check_service_health(service_name):
            logger.info(f"{service['name']} started successfully")
            return True
        else:
            logger.error(f"{service['name']} failed to start or is not healthy")
            return False
    except Exception as e:
        logger.error(f"Error starting {service['name']}: {str(e)}")
        return False

# Stop a service
def stop_service(service_name):
    """Stop a specific service"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    
    if not service.get("required", True):
        logger.info(f"Skipping {service['name']} (not required)")
        return True
    
    logger.info(f"Stopping {service['name']}...")
    
    # Check if the service is running
    if not is_service_running(service_name):
        logger.info(f"{service['name']} is not running")
        return True
    
    # Stop the service
    try:
        if platform.system() == "Windows":
            if service_name == "chromadb":
                # For ChromaDB on Windows, find and kill the process
                subprocess.run(
                    f"taskkill /F /FI \"WINDOWTITLE eq chroma*\"",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                subprocess.run(
                    f"taskkill /F /IM chroma.exe",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif service_name == "fastapi":
                # For FastAPI on Windows, find and kill the process
                subprocess.run(
                    f"taskkill /F /FI \"WINDOWTITLE eq uvicorn app:app*\"",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                subprocess.run(
                    f"taskkill /F /IM uvicorn.exe",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
        else:
            # Unix-specific stop command
            if service_name == "chromadb":
                subprocess.run(
                    "pkill -f 'chroma run'",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif service_name == "fastapi":
                subprocess.run(
                    "pkill -f 'uvicorn app:app'",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
        
        # Wait for the service to stop
        time.sleep(2)
        
        # Check if the service is still running
        if is_service_running(service_name):
            logger.error(f"{service['name']} failed to stop")
            return False
        else:
            logger.info(f"{service['name']} stopped successfully")
            return True
    except Exception as e:
        logger.error(f"Error stopping {service['name']}: {e}")
        return False

# Check service health
def check_service_health(service_name):
    """Check health of a specific service"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    logger.info(f"Checking health of {service['name']}...")
    
    try:
        if service["health_check"]():
            logger.info(f"{service['name']} is healthy")
            return True
        else:
            logger.error(f"{service['name']} is not healthy")
            return False
    except Exception as e:
        logger.error(f"{service['name']} health check failed: {e}")
        return False

# Setup function
def setup():
    """Setup StudyIndexer services"""
    logger.info("Setting up StudyIndexer services...")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed")
        return False
    
    # Initialize ChromaDB collection
    if not init_chroma_collection():
        logger.error("ChromaDB collection initialization failed")
        return False
    
    logger.info("Setup completed successfully")
    return True

# Start all services
def start_all():
    """Start all StudyIndexer services"""
    logger.info("Starting all StudyIndexer services...")
    
    # Setup first
    if not setup():
        logger.error("Setup failed, cannot start services")
        return False
    
    # Start services in order
    success = True
    
    # Start ChromaDB first
    if "chromadb" in SERVICES and SERVICES["chromadb"]["required"]:
        if not start_service("chromadb"):
            logger.error("Failed to start ChromaDB")
            if SERVICES["chromadb"]["required"]:
                logger.error("ChromaDB is required, aborting startup")
                return False
            success = False
    
    # Start FastAPI last
    if "fastapi" in SERVICES:
        if not start_service("fastapi"):
            logger.error("Failed to start FastAPI")
            success = False
    
    if success:
        logger.info("All services started successfully")
    else:
        logger.warning("Some services failed to start")
    
    return success

# Stop all services
def stop_all():
    """Stop all StudyIndexer services"""
    logger.info("Stopping all StudyIndexer services...")
    
    # Stop services in reverse order
    success = True
    
    # Stop FastAPI first
    if "fastapi" in SERVICES:
        if not stop_service("fastapi"):
            logger.error("Failed to stop FastAPI")
            success = False
    
    # Stop ChromaDB last
    if "chromadb" in SERVICES:
        if not stop_service("chromadb"):
            logger.error("Failed to stop ChromaDB")
            success = False
    
    if success:
        logger.info("All services stopped successfully")
    else:
        logger.warning("Some services failed to stop")
    
    return success

# Check health of all services
def check_all_health():
    """Check health of all StudyIndexer services"""
    logger.info("Checking health of all StudyIndexer services...")
    
    # Check services in order
    all_healthy = True
    
    # Check ChromaDB
    if "chromadb" in SERVICES:
        if not check_service_health("chromadb"):
            logger.error("ChromaDB is not healthy")
            all_healthy = False
    
    # Check FastAPI
    if "fastapi" in SERVICES:
        if not check_service_health("fastapi"):
            logger.error("FastAPI is not healthy")
            all_healthy = False
    
    if all_healthy:
        logger.info("All services are healthy")
    else:
        logger.warning("Some services are not healthy")
    
    return all_healthy

# Display service information
def display_service_info():
    """Display information about StudyIndexer services"""
    logger.info("StudyIndexer Service Information")
    logger.info("===============================")
    
    # Display environment information
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    
    # Display service information
    logger.info("\nConfigured Services:")
    for name, service in SERVICES.items():
        logger.info(f"- {service['name']} ({name}):")
        logger.info(f"  - Command: {service['start_cmd']}")
        logger.info(f"  - Health URL: {service.get('health_url', 'N/A')}")
        logger.info(f"  - Required: {service.get('required', True)}")
    
    # Display environment variables
    logger.info("\nEnvironment Variables:")
    logger.info(f"- HOST: {get_env('HOST', '0.0.0.0')}")
    logger.info(f"- PORT: {get_env('PORT', '8081')}")
    logger.info(f"- DEBUG: {get_env('DEBUG', 'false')}")
    logger.info(f"- CHROMA_HOST: {get_env('CHROMA_HOST', '0.0.0.0')}")
    logger.info(f"- CHROMA_PORT: {get_env('CHROMA_PORT', '8000')}")
    logger.info(f"- CHROMA_PERSIST_DIR: {get_env('CHROMA_PERSIST_DIR', './data/chroma')}")
    
    # Check current service status
    logger.info("\nCurrent Service Status:")
    
    # Check ChromaDB
    try:
        if "chromadb" in SERVICES and SERVICES["chromadb"]["health_check"]():
            logger.info("- ChromaDB: Running")
        else:
            logger.info("- ChromaDB: Stopped")
    except Exception:
        logger.info("- ChromaDB: Stopped")
    
    # Check FastAPI
    try:
        if "fastapi" in SERVICES and SERVICES["fastapi"]["health_check"]():
            logger.info("- FastAPI: Running")
        else:
            logger.info("- FastAPI: Stopped")
    except Exception:
        logger.info("- FastAPI: Stopped")
    
    logger.info("\nFor more information, run with --help")

def print_service_info():
    """Print detailed information about services"""
    logger.info("StudyIndexer Service Information")
    logger.info("===============================")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    
    logger.info("\nConfigured Services:")
    for service_name, service in SERVICES.items():
        logger.info(f"- {service['name']} ({service_name}):")
        logger.info(f"  - Command: {service['start_cmd']}")
        logger.info(f"  - Health URL: {service['health_url']}")
        logger.info(f"  - Required: {service.get('required', True)}")
    
    logger.info("\nEnvironment Variables:")
    for key in ["HOST", "PORT", "DEBUG", "CHROMA_HOST", "CHROMA_PORT", "CHROMA_PERSIST_DIR"]:
        logger.info(f"- {key}: {os.getenv(key)}")
    
    logger.info("\nCurrent Service Status:")
    for service_name in SERVICES:
        status = "Running" if is_service_running(service_name) else "Stopped"
        logger.info(f"- {service_name}: {status}")
        
        # Add API tools information if FastAPI is running
        if service_name == "fastapi" and status == "Running":
            host = os.getenv("HOST", "127.0.0.1")
            port = os.getenv("PORT", "8081")
            logger.info("\nAPI Tools:")
            logger.info(f"- API Explorer: http://{host}:{port}/explorer")
            logger.info(f"- Swagger UI: http://{host}:{port}/docs")
            logger.info(f"- ReDoc: http://{host}:{port}/redoc")
    
    logger.info("\nFor more information, run with --help")

# Main function
def main():
    """Main function"""
    load_env_files()
    
    parser = argparse.ArgumentParser(description="StudyIndexer Service Manager")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "info"],
                      help="Command to execute")
    args = parser.parse_args()
    
    if args.command == "start":
        start_all()
    elif args.command == "stop":
        stop_all()
    elif args.command == "restart":
        stop_all()
        start_all()
    elif args.command == "status":
        check_all_health()
    elif args.command == "info":
        print_service_info()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
