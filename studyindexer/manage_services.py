#!/usr/bin/env python3
"""
StudyIndexerNew Service Manager
----------------------------
A script to manage StudyIndexerNew services.
"""
import os
import sys
import time
import signal
import argparse
import subprocess
import requests
import logging
import platform
from pathlib import Path
from dotenv import load_dotenv
import socket
import psutil  # Add psutil import for process management

# Get the absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Configure logging with absolute paths
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "service-manager.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("service-manager")

# Load environment variables
def load_env_files():
    """Load environment variables from .env files"""
    # Load main .env file
    env_file = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_file):
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
        "start_cmd": f"chroma run --host 127.0.0.1 --port {get_env('CHROMA_PORT', '8000')} --path {os.path.join(PROJECT_ROOT, get_env('CHROMA_PERSIST_DIR', 'data/chroma'))}",
        "health_url": f"http://127.0.0.1:{get_env('CHROMA_PORT', '8000')}/api/v1/heartbeat",
        "health_check": lambda: requests.get(f"http://127.0.0.1:{get_env('CHROMA_PORT', '8000')}/api/v1/heartbeat", timeout=5).status_code == 200,
        "required": True,
        "startup_time": 10
    },
    "fastapi": {
        "name": "FastAPI Server",
        "start_cmd": f"python -m uvicorn main:app --host 127.0.0.1 --port {get_env('PORT', '8081')} {'--reload' if get_env('DEBUG', 'true').lower() == 'true' else ''}",
        "health_url": f"http://127.0.0.1:{get_env('PORT', '8081')}/",
        "health_check": lambda: requests.get(f"http://127.0.0.1:{get_env('PORT', '8081')}/", timeout=5).status_code == 200,
        "required": True,
        "startup_time": 5
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
        logger.info("All required Python packages are installed")
    except ImportError as e:
        logger.error(f"Missing Python package: {e}")
        logger.error("Please install all required packages: pip install -r requirements.txt")
        return False
    
    # Check if directories exist with absolute paths
    data_dir = os.path.join(PROJECT_ROOT, "data")
    if not os.path.exists(data_dir):
        logger.info(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    chroma_dir = os.path.join(PROJECT_ROOT, "data", "chroma")
    if not os.path.exists(chroma_dir):
        logger.info(f"Creating ChromaDB directory: {chroma_dir}")
        os.makedirs(chroma_dir, exist_ok=True)
    
    # All prerequisites satisfied
    logger.info("All prerequisites are satisfied")
    return True

# Check if a service is running
def is_service_running(service_name):
    """Check if a service is running"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    
    try:
        # For FastAPI, just check if the port is in use as a quick health check
        if service_name == "fastapi":
            port = int(get_env('PORT', '8081'))
            # If port is in use, consider the service running
            # This assumes that if something is on port 8081, it's our FastAPI service
            return is_port_in_use(port)
        
        # For all other services, use HTTP health check
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
    
    logger.info(f"Starting {service['name']}...")
    
    # Check if the service is already running
    if is_service_running(service_name):
        logger.info(f"{service['name']} is already running")
        return True
    
    # Check if port is in use
    port = int(get_env('CHROMA_PORT', '8000')) if service_name == "chromadb" else int(get_env('PORT', '8081'))
    if is_port_in_use(port):
        # For FastAPI, try basic process killing without complex checks
        if service_name == "fastapi":
            logger.warning(f"Port {port} is in use. Attempting to kill existing process...")
            try:
                if platform.system() == "Windows":
                    subprocess.run(f"taskkill /F /IM uvicorn.exe", shell=True, stderr=subprocess.PIPE)
                else:
                    subprocess.run("pkill -f uvicorn", shell=True, stderr=subprocess.PIPE)
                    subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to kill process on port {port}: {e}")
                
            # Check again if port is free
            if is_port_in_use(port):
                logger.error(f"Port {port} is still in use. Cannot start {service['name']}")
                return False
        else:
            logger.error(f"Port {port} is already in use. Cannot start {service['name']}")
            return False
    
    # Start the service
    try:
        log_file = os.path.join(LOGS_DIR, f"{service_name}.log")
        
        if platform.system() == "Windows":
            # Windows-specific start command
            cmd = f"start /B {service['start_cmd']} > \"{log_file}\" 2>&1"
            subprocess.Popen(cmd, shell=True, cwd=PROJECT_ROOT)
        else:
            # Unix-specific start command
            cmd = f"cd \"{PROJECT_ROOT}\" && nohup {service['start_cmd']} > \"{log_file}\" 2>&1 &"
            subprocess.Popen(cmd, shell=True)
        
        logger.info(f"{service['name']} started")
        
        # Wait for the service to start
        startup_time = service.get("startup_time", 5)
        logger.info(f"Waiting {startup_time} seconds for {service['name']} to start...")
        time.sleep(startup_time)
        
        # Check if the service is healthy
        if is_service_running(service_name):
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
    
    logger.info(f"Stopping {service['name']}...")
    
    # Check if the service is running
    if not is_service_running(service_name):
        logger.info(f"{service['name']} is not running")
        return True
    
    # Stop the service - simple approach without complex process detection
    try:
        if platform.system() == "Windows":
            if service_name == "chromadb":
                subprocess.run(f"taskkill /F /IM chroma.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif service_name == "fastapi":
                subprocess.run(f"taskkill /F /IM uvicorn.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # Unix-specific stop command
            if service_name == "chromadb":
                subprocess.run("pkill -f 'chroma run'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # Also free the port
                port = int(get_env('CHROMA_PORT', '8000'))
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
            elif service_name == "fastapi":
                subprocess.run("pkill -f 'uvicorn main:app'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run("pkill -f uvicorn", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # Also free the port
                port = int(get_env('PORT', '8081'))
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
        
        # Wait for the service to stop
        time.sleep(2)
        
        # Check if the service is still running by checking if port is free
        port = int(get_env('CHROMA_PORT', '8000')) if service_name == "chromadb" else int(get_env('PORT', '8081'))
        if is_port_in_use(port):
            logger.warning(f"Port {port} is still in use. Trying forceful kill...")
            if platform.system() != "Windows":
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
            time.sleep(1)
            
            if is_port_in_use(port):
                logger.error(f"{service['name']} failed to stop. Port {port} still in use.")
                return False
            
        logger.info(f"{service['name']} stopped successfully")
        return True
    except Exception as e:
        logger.error(f"Error stopping {service['name']}: {e}")
        return False

# Start all services
def start_all():
    """Start all StudyIndexerNew services"""
    logger.info("Starting all StudyIndexerNew services...")
    
    # Create required directories without full prerequisite check
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "chroma"), exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Start services in order
    success = True
    
    # Start ChromaDB first
    if not start_service("chromadb"):
        logger.error("Failed to start ChromaDB")
        return False
    
    # Start FastAPI last
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
    """Stop all StudyIndexerNew services"""
    logger.info("Stopping all StudyIndexerNew services...")
    
    # Stop services in reverse order
    success = True
    
    # Stop FastAPI first
    if not stop_service("fastapi"):
        logger.error("Failed to stop FastAPI")
        success = False
    
    # Stop ChromaDB last
    if not stop_service("chromadb"):
        logger.error("Failed to stop ChromaDB")
        success = False
    
    if success:
        logger.info("All services stopped successfully")
    else:
        logger.warning("Some services failed to stop")
    
    return success

# Check status of all services
def check_status():
    """Check status of all StudyIndexerNew services"""
    logger.info("Checking status of all StudyIndexerNew services...")
    
    all_running = True
    
    # Check ChromaDB
    if is_service_running("chromadb"):
        logger.info("ChromaDB is running")
    else:
        logger.warning("ChromaDB is not running")
        all_running = False
    
    # Check FastAPI
    if is_service_running("fastapi"):
        logger.info("FastAPI is running")
    else:
        logger.warning("FastAPI is not running")
        all_running = False
    
    if all_running:
        logger.info("All services are running")
    else:
        logger.warning("Some services are not running")
    
    return all_running

# Display service information
def show_info():
    """Display information about StudyIndexerNew services"""
    logger.info("StudyIndexerNew Service Information")
    logger.info("===================================")
    
    # Display environment information
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Display service information
    logger.info("\nConfigured Services:")
    for name, service in SERVICES.items():
        logger.info(f"- {service['name']} ({name}):")
        logger.info(f"  - Command: {service['start_cmd']}")
        logger.info(f"  - Health URL: {service.get('health_url', 'N/A')}")
    
    # Display environment variables
    logger.info("\nEnvironment Variables:")
    logger.info(f"- PORT: {get_env('PORT', '8081')}")
    logger.info(f"- DEBUG: {get_env('DEBUG', 'true')}")
    logger.info(f"- CHROMA_PORT: {get_env('CHROMA_PORT', '8000')}")
    logger.info(f"- CHROMA_PERSIST_DIR: {get_env('CHROMA_PERSIST_DIR', './data/chroma')}")
    
    # Display log locations
    logger.info("\nLog Locations:")
    logger.info(f"- Service Manager Log: {os.path.join(LOGS_DIR, 'service-manager.log')}")
    logger.info(f"- ChromaDB Log: {os.path.join(LOGS_DIR, 'chromadb.log')}")
    logger.info(f"- FastAPI Log: {os.path.join(LOGS_DIR, 'fastapi.log')}")
    
    # Check current service status
    logger.info("\nCurrent Service Status:")
    
    # Check ChromaDB
    if is_service_running("chromadb"):
        logger.info("- ChromaDB: Running")
    else:
        logger.info("- ChromaDB: Stopped")
    
    # Check FastAPI
    if is_service_running("fastapi"):
        logger.info("- FastAPI: Running")
        logger.info(f"\nAPI Documentation: http://127.0.0.1:{get_env('PORT', '8081')}/docs")
    else:
        logger.info("- FastAPI: Stopped")

# Start FastAPI manually for debugging
def start_fastapi_debug():
    """Start FastAPI in debug mode with direct console output"""
    logger.info("Starting FastAPI in debug mode...")
    
    # Kill any existing processes first
    port = int(get_env('PORT', '8081'))
    if is_port_in_use(port):
        logger.warning(f"Port {port} is in use. Attempting to kill existing process...")
        try:
            if platform.system() != "Windows":
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
                subprocess.run("pkill -f uvicorn", shell=True, stderr=subprocess.PIPE)
            time.sleep(2)
        except Exception as e:
            logger.error(f"Failed to kill process on port {port}: {e}")
    
    # Start FastAPI directly
    cmd = f"cd \"{PROJECT_ROOT}\" && python -m uvicorn main:app --host 127.0.0.1 --port {port}"
    logger.info(f"Running command: {cmd}")
    
    # This will block and show output directly in the console
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        logger.info("FastAPI debug mode stopped by user")
        return

# Main function
def main():
    """Main function"""
    load_env_files()
    
    parser = argparse.ArgumentParser(description="StudyIndexerNew Service Manager")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "info", "debug-fastapi"],
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
        check_status()
    elif args.command == "info":
        show_info()
    elif args.command == "debug-fastapi":
        start_fastapi_debug()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 