#!/usr/bin/env python3
"""
Simple Service Manager for StudyIndexer
This script manages the ChromaDB and FastAPI services with minimal dependencies.
"""

import os
import sys
import time
import socket
import subprocess
import logging
import signal
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/service_manager.log')
    ]
)
logger = logging.getLogger('service-manager')

# Create logs directory if it doesn't exist
Path("logs").mkdir(parents=True, exist_ok=True)

# Load environment variables
def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path('../.env')
    if env_path.exists():
        logger.info(f"Loading environment from {env_path.absolute()}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.info("No .env file found, using system environment variables")
    return os.environ

# Get environment variable with default
def get_env(key, default=None):
    """Get environment variable with default value"""
    return os.environ.get(key, default)

# Get environment variable as integer with default
def get_env_int(key, default=None):
    """Get environment variable as integer with default value"""
    value = get_env(key)
    if value is None:
        return int(default) if default is not None else None
    try:
        return int(value)
    except ValueError:
        return int(default) if default is not None else None

# Check if a port is in use
def is_port_in_use(port, host='127.0.0.1'):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

# Check if a process is running
def is_process_running(process_name):
    """Check if a process is running by name"""
    try:
        if sys.platform == "win32":
            output = subprocess.check_output(f"tasklist /FI \"IMAGENAME eq {process_name}*\"", shell=True)
            return process_name in output.decode()
        else:
            output = subprocess.check_output(f"pgrep -f {process_name}", shell=True)
            return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

# Start ChromaDB
def start_chromadb():
    """Start ChromaDB service"""
    logger.info("Starting ChromaDB...")
    
    # Check if already running
    chroma_port = get_env_int("CHROMA_PORT", 8000)
    if is_port_in_use(chroma_port):
        logger.info(f"Port {chroma_port} is already in use. ChromaDB may already be running.")
        return True
    
    # Create data directory if it doesn't exist
    chroma_data_dir = get_env("CHROMA_PERSIST_DIR", "./data/chroma")
    Path(chroma_data_dir).mkdir(parents=True, exist_ok=True)
    
    # Start ChromaDB
    try:
        chroma_host = get_env("CHROMA_HOST", "127.0.0.1")
        cmd = f"chroma run --host {chroma_host} --port {chroma_port} --path {chroma_data_dir}"
        
        if sys.platform == "win32":
            subprocess.Popen(f"start /B {cmd} > logs\\chromadb.log 2>&1", shell=True)
        else:
            subprocess.Popen(f"nohup {cmd} > logs/chromadb.log 2>&1 &", shell=True)
        
        logger.info(f"ChromaDB starting on {chroma_host}:{chroma_port}")
        
        # Wait for ChromaDB to start
        startup_time = get_env_int("CHROMA_STARTUP_TIME", 15)
        logger.info(f"Waiting {startup_time} seconds for ChromaDB to start...")
        time.sleep(startup_time)
        
        # Verify ChromaDB is running
        try:
            response = requests.get(f"http://{chroma_host}:{chroma_port}/api/v2/heartbeat", timeout=5)
            if response.status_code == 200:
                logger.info("ChromaDB started successfully")
                return True
            else:
                logger.error(f"ChromaDB health check failed with status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    except Exception as e:
        logger.error(f"Error starting ChromaDB: {e}")
        return False

# Start FastAPI
def start_fastapi():
    """Start FastAPI service"""
    logger.info("Starting FastAPI server...")
    
    # Check if already running
    api_port = get_env_int("PORT", 8081)
    if is_port_in_use(api_port):
        logger.info(f"Port {api_port} is already in use. FastAPI may already be running.")
        return True
    
    # Start FastAPI
    try:
        api_host = get_env("HOST", "127.0.0.1")
        
        # Make sure ChromaDB is running before starting FastAPI
        chroma_port = get_env_int("CHROMA_PORT", 8000)
        if not is_port_in_use(chroma_port):
            logger.error("ChromaDB is not running. FastAPI requires ChromaDB to be running.")
            return False
        
        # Use the dedicated script to start FastAPI
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_fastapi.py")
        
        if sys.platform == "win32":
            # Windows
            process = subprocess.Popen(
                ["python", script_path],
                stdout=open("logs\\fastapi.log", "w"),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # Linux/Mac
            process = subprocess.Popen(
                ["python", script_path],
                stdout=open("logs/fastapi.log", "w"),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
        
        logger.info(f"FastAPI starting on {api_host}:{api_port}")
        
        # Wait for FastAPI to start
        startup_time = get_env_int("FASTAPI_STARTUP_TIME", 15)
        logger.info(f"Waiting {startup_time} seconds for FastAPI to start...")
        time.sleep(startup_time)
        
        # Verify FastAPI is running
        try:
            health_endpoint = get_env("FASTAPI_HEALTH_ENDPOINT", "/api/health")
            response = requests.get(f"http://{api_host}:{api_port}{health_endpoint}", timeout=5)
            if response.status_code == 200:
                logger.info("FastAPI started successfully")
                return True
            else:
                logger.error(f"FastAPI health check failed with status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"FastAPI health check failed: {e}")
            return False
    except Exception as e:
        logger.error(f"Error starting FastAPI: {e}")
        return False

# Stop ChromaDB
def stop_chromadb():
    """Stop ChromaDB service"""
    logger.info("Stopping ChromaDB...")
    
    try:
        if sys.platform == "win32":
            subprocess.run("taskkill /F /FI \"WINDOWTITLE eq chroma*\"", shell=True)
            subprocess.run("taskkill /F /IM chroma.exe", shell=True)
        else:
            subprocess.run("pkill -f 'chroma run'", shell=True)
        
        # Wait for the process to stop
        time.sleep(2)
        
        # Verify it's stopped
        chroma_port = get_env_int("CHROMA_PORT", 8000)
        if not is_port_in_use(chroma_port):
            logger.info("ChromaDB stopped successfully")
            return True
        else:
            logger.error("Failed to stop ChromaDB")
            return False
    except Exception as e:
        logger.error(f"Error stopping ChromaDB: {e}")
        return False

# Stop FastAPI
def stop_fastapi():
    """Stop FastAPI service"""
    logger.info("Stopping FastAPI server...")
    
    try:
        if sys.platform == "win32":
            subprocess.run("taskkill /F /FI \"WINDOWTITLE eq uvicorn app:app*\"", shell=True)
            subprocess.run("taskkill /F /IM uvicorn.exe", shell=True)
        else:
            subprocess.run("pkill -f 'uvicorn app:app'", shell=True)
        
        # Wait for the process to stop
        time.sleep(2)
        
        # Verify it's stopped
        api_port = get_env_int("PORT", 8081)
        if not is_port_in_use(api_port):
            logger.info("FastAPI stopped successfully")
            return True
        else:
            logger.error("Failed to stop FastAPI")
            return False
    except Exception as e:
        logger.error(f"Error stopping FastAPI: {e}")
        return False

# Start all services
def start_all():
    """Start all services"""
    logger.info("Starting all services...")
    
    # Start ChromaDB
    chromadb_success = start_chromadb()
    
    # Start FastAPI (independent of ChromaDB success)
    fastapi_success = start_fastapi()
    
    if chromadb_success and fastapi_success:
        logger.info("All services started successfully")
        return True
    else:
        logger.warning("Some services failed to start")
        return False

# Stop all services
def stop_all():
    """Stop all services"""
    logger.info("Stopping all services...")
    
    # Stop FastAPI first
    fastapi_success = stop_fastapi()
    
    # Stop ChromaDB
    chromadb_success = stop_chromadb()
    
    if fastapi_success and chromadb_success:
        logger.info("All services stopped successfully")
        return True
    else:
        logger.warning("Some services failed to stop")
        return False

# Restart all services
def restart_all():
    """Restart all services"""
    logger.info("Restarting all services...")
    
    # Stop all services
    stop_all()
    
    # Start all services
    return start_all()

# Check status of all services
def status_all():
    """Check status of all services"""
    logger.info("Checking status of all services...")
    
    # Check ChromaDB
    chroma_port = get_env_int("CHROMA_PORT", 8000)
    chroma_running = is_port_in_use(chroma_port)
    
    # Check FastAPI
    api_port = get_env_int("PORT", 8081)
    api_running = is_port_in_use(api_port)
    
    # Print status
    logger.info(f"ChromaDB: {'RUNNING' if chroma_running else 'STOPPED'}")
    logger.info(f"FastAPI: {'RUNNING' if api_running else 'STOPPED'}")
    
    return {
        "chromadb": chroma_running,
        "fastapi": api_running
    }

# Main function
def main():
    """Main function"""
    # Load environment variables
    load_env_file()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python service_manager.py [start|stop|restart|status]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_all()
    elif command == "stop":
        stop_all()
    elif command == "restart":
        restart_all()
    elif command == "status":
        status_all()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python service_manager.py [start|stop|restart|status]")

# Run main function
if __name__ == "__main__":
    main() 