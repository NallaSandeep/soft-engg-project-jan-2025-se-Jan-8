#!/usr/bin/env python3
"""
Simple standalone script to start the FastAPI server.
"""

import os
import sys
import signal
import uvicorn

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env"))

# Get environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8081"))

def is_port_in_use(port, host='127.0.0.1'):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\nShutting down FastAPI server...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if FastAPI is already running
    if is_port_in_use(PORT):
        print(f"FastAPI is already running on port {PORT}")
        sys.exit(0)
    
    # Set the current working directory to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start FastAPI
    print(f"Starting FastAPI server on {HOST}:{PORT}")
    
    # Run the FastAPI server
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        log_level="info"
    ) 