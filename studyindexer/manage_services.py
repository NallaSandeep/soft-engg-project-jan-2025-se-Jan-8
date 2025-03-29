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
import concurrent.futures  # Add for parallel service operations

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
        "health_check": lambda: requests.get(f"http://127.0.0.1:{get_env('CHROMA_PORT', '8000')}/api/v1/heartbeat", timeout=2).status_code == 200,
        "port": int(get_env('CHROMA_PORT', '8000')),
        "required": True,
        "max_startup_time": 15,  # Maximum seconds to wait for service to start
        "process_name": "chroma" if platform.system() == "Windows" else "chroma run"
    },
    "fastapi": {
        "name": "FastAPI Server",
        "start_cmd": f"python -m uvicorn main:app --host 127.0.0.1 --port {get_env('PORT', '8081')} {'--reload' if get_env('DEBUG', 'true').lower() == 'true' else ''}",
        "health_url": f"http://127.0.0.1:{get_env('PORT', '8081')}/",
        "health_check": lambda: requests.get(f"http://127.0.0.1:{get_env('PORT', '8081')}/", timeout=2).status_code == 200,
        "port": int(get_env('PORT', '8081')),
        "required": True,
        "max_startup_time": 8,  # Maximum seconds to wait for service to start
        "process_name": "uvicorn" if platform.system() == "Windows" else "uvicorn main:app"
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

# Find and kill process by port
def kill_process_by_port(port):
    """Kill process using specific port with simple commands for WSL"""
    try:
        # Simple Linux/WSL approach
        subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        logger.warning(f"Error in kill_process_by_port: {e}")
    return False

# Check if a service is running
def is_service_running(service_name, retry_count=2, retry_delay=0.5):
    """Check if a service is running with retries"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    port = service["port"]
    
    # First just check if the port is in use
    if not is_port_in_use(port):
        return False
    
    # Always try an actual HTTP check for both services
    for attempt in range(retry_count):
        try:
            response = requests.get(service["health_url"], timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            if attempt < retry_count - 1:
                time.sleep(retry_delay)
    
    # If we reach here, the port is in use but HTTP check failed
    logger.warning(f"Port {port} is in use but {service['name']} health check failed")
    return False

# Start a service
def start_service(service_name):
    """Start a specific service"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    
    logger.info(f"Starting {service['name']}...")
    
    # Kill any existing process on the port to ensure clean start
    # Don't check if service is running first, just clean the port
    port = service["port"]
    if is_port_in_use(port):
        logger.info(f"Killing any process using port {port} before starting {service['name']}")
        kill_process_by_port(port)
        time.sleep(1)
        
        # Check again if port is free
        if is_port_in_use(port):
            logger.error(f"Port {port} is still in use. Cannot start {service['name']}")
            return False
    
    # Start the service
    try:
        log_file = os.path.join(LOGS_DIR, f"{service_name}.log")
        
        # WSL start command
        cmd = f"cd \"{PROJECT_ROOT}\" && nohup {service['start_cmd']} > \"{log_file}\" 2>&1 &"
        subprocess.Popen(cmd, shell=True)
        
        logger.info(f"{service['name']} starting...")
        
        # Use longer wait times for WSL environment
        wait_time = 15 if service_name == "fastapi" else 12
        logger.info(f"Waiting {wait_time} seconds for {service['name']} to start...")
        time.sleep(wait_time)
        
        # Verify the service is actually running with HTTP check with more retries for FastAPI
        retry_count = 5 if service_name == "fastapi" else 2
        retry_delay = 3 if service_name == "fastapi" else 0.5
        
        if is_service_running(service_name, retry_count=retry_count, retry_delay=retry_delay):
            logger.info(f"{service['name']} started successfully")
            return True
        else:
            logger.error(f"{service['name']} failed to start properly - check logs")
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
    
    # Check if the service is running by port check only
    port = service["port"]
    if not is_port_in_use(port):
        logger.info(f"{service['name']} is not running")
        return True
    
    # Unix-specific stop command
    if service_name == "chromadb":
        # Try multiple commands for ChromaDB in WSL
        subprocess.run("pkill -f 'chroma'", shell=True, stderr=subprocess.PIPE)
        subprocess.run("pkill -f 'chromadb'", shell=True, stderr=subprocess.PIPE)
        # Force-free the port for ChromaDB
        for i in range(3):  # Try multiple times with increasing force
            subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
            if not is_port_in_use(port):
                break
            time.sleep(0.5)
    elif service_name == "fastapi":
        subprocess.run("pkill -f 'uvicorn'", shell=True, stderr=subprocess.PIPE)
        subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.PIPE)
    
    # Allow a moment for the process to terminate
    time.sleep(1)
    
    # For ChromaDB, accept that it might not fully stop and continue anyway
    if service_name == "chromadb" and is_port_in_use(port):
        logger.warning(f"ChromaDB may still be running (port {port} is still in use). Continuing anyway.")
        return True
    
    # Verify the port is free now
    if is_port_in_use(port):
        logger.warning(f"{service['name']} may still be running (port {port} is still in use)")
        return False
    
    logger.info(f"{service['name']} stopped successfully")
    return True

# Start all services
def start_all():
    """Start all StudyIndexerNew services"""
    logger.info("Starting all StudyIndexerNew services...")
    
    # Create required directories
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "chroma"), exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Always forcefully kill all existing services first
    stop_all(force=True)
    
    # Clear log files to ensure fresh logs
    try:
        # Clear existing log files for services to avoid confusion
        open(os.path.join(LOGS_DIR, "chromadb.log"), 'w').close()
        open(os.path.join(LOGS_DIR, "fastapi.log"), 'w').close()
    except Exception as e:
        logger.warning(f"Failed to clear log files: {e}")
    
    # Explicitly wait to ensure all processes are stopped
    time.sleep(2)
    
    # Start ChromaDB first
    logger.info("Starting ChromaDB server...")
    if not start_service("chromadb"):
        logger.error("Failed to start ChromaDB")
        return False
    
    # Wait and verify ChromaDB actually started - essential for FastAPI
    for attempt in range(3):
        try:
            logger.info("Verifying ChromaDB is responding...")
            response = requests.get(SERVICES["chromadb"]["health_url"], timeout=2)
            if response.status_code == 200:
                logger.info("ChromaDB is responding correctly")
                break
        except requests.RequestException:
            if attempt < 2:
                logger.warning("ChromaDB not responding yet, waiting 3 more seconds...")
                time.sleep(3)
            else:
                logger.error("ChromaDB failed to respond to health check - FastAPI will likely fail")
    
    # Then start FastAPI with longer timeout
    logger.info("Starting FastAPI server...")
    if not start_service("fastapi"):
        # Even if FastAPI reports failure, it might still be initializing
        logger.warning("FastAPI reported failure but might still be starting up...")
        logger.warning("Run 'python manage_services.py status' in a few seconds to check if it completes initialization")
        
        # Start status polling in the background
        poll_status_in_background()
        return False
    
    # Wait for services to fully initialize
    logger.info("Waiting for services to fully initialize...")
    time.sleep(3)
    
    logger.info("All services started successfully")
    return True

# Stop all services
def stop_all(force=False):
    """Stop all StudyIndexerNew services"""
    logger.info("Stopping all StudyIndexerNew services...")
    
    # More aggressive brute force killing of all related processes
    try:
        # Kill FastAPI processes
        subprocess.run("pkill -f 'uvicorn main:app'", shell=True, stderr=subprocess.PIPE)
        subprocess.run("pkill -f uvicorn", shell=True, stderr=subprocess.PIPE)
        
        # Kill ChromaDB processes 
        subprocess.run("pkill -f 'chroma'", shell=True, stderr=subprocess.PIPE)
        subprocess.run("pkill -f 'chromadb'", shell=True, stderr=subprocess.PIPE)
        
        # Free ports directly with maximum force
        subprocess.run(f"fuser -k {SERVICES['fastapi']['port']}/tcp", shell=True, stderr=subprocess.PIPE)
        subprocess.run(f"fuser -k {SERVICES['chromadb']['port']}/tcp", shell=True, stderr=subprocess.PIPE)
        
        # Try one more time with force if specified
        if force:
            subprocess.run(f"fuser -k -9 {SERVICES['fastapi']['port']}/tcp", shell=True, stderr=subprocess.PIPE)
            subprocess.run(f"fuser -k -9 {SERVICES['chromadb']['port']}/tcp", shell=True, stderr=subprocess.PIPE)
        
        # Give processes time to terminate
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Error in brute force process killing: {e}")
    
    # Then do the normal stop procedures
    services_stopped = True
    
    # First stop FastAPI
    if not stop_service("fastapi"):
        logger.error("Failed to stop FastAPI")
        services_stopped = False
    
    # Then stop ChromaDB
    if not stop_service("chromadb"):
        logger.error("Failed to stop ChromaDB")
        services_stopped = False
    
    # Final check - make sure the ports are definitely free
    fastapi_port_free = not is_port_in_use(SERVICES['fastapi']['port'])
    chroma_port_free = not is_port_in_use(SERVICES['chromadb']['port'])
    
    if not fastapi_port_free:
        logger.warning(f"FastAPI port {SERVICES['fastapi']['port']} still in use after stop attempts")
    
    if not chroma_port_free:
        logger.warning(f"ChromaDB port {SERVICES['chromadb']['port']} still in use after stop attempts")
    
    if fastapi_port_free and chroma_port_free:
        logger.info("All ports verified free - services successfully stopped")
    
    return services_stopped

# Check status of all services
def check_status():
    """Check status of all StudyIndexerNew services"""
    logger.info("Checking status of all StudyIndexerNew services...")
    
    all_running = True
    
    # Simple sequential check for each service
    for service_name in SERVICES:
        running = is_service_running(service_name)
        if running:
            logger.info(f"{SERVICES[service_name]['name']} is running")
        else:
            logger.warning(f"{SERVICES[service_name]['name']} is not running")
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
        kill_process_by_port(port)
    
    # Start FastAPI directly
    cmd = f"cd \"{PROJECT_ROOT}\" && python -m uvicorn main:app --host 127.0.0.1 --port {port}"
    logger.info(f"Running command: {cmd}")
    
    # This will block and show output directly in the console
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        logger.info("FastAPI debug mode stopped by user")
        return

# Poll status in background and display result
def poll_status_in_background():
    """Start a background process to check service status after delay"""
    try:
        # Use a simple bash script to wait and then run status check
        cmd = f"sleep 15 && echo '\n\n---- Automatic status check after delay ----' && python {os.path.join(PROJECT_ROOT, 'manage_services.py')} status"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        logger.warning(f"Could not start background status polling: {e}")

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
        if start_all() is False:
            print("\nNOTE: If FastAPI is still starting up, wait 15 seconds and check again with:")
            print("    python manage_services.py status")
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