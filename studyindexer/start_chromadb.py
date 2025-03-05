#!/usr/bin/env python3
"""
Simple standalone script to start ChromaDB.
"""

import os
import sys
import time
import subprocess
import requests
import signal

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env"))

# Get environment variables
CHROMA_HOST = os.getenv("CHROMA_HOST", "0.0.0.0")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
CHROMA_HEALTH_ENDPOINT = os.getenv("CHROMA_HEALTH_ENDPOINT", "/api/v2/heartbeat")

def is_port_in_use(port, host='127.0.0.1'):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\nShutting down ChromaDB...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if ChromaDB is already running
    if is_port_in_use(CHROMA_PORT):
        print(f"ChromaDB is already running on port {CHROMA_PORT}")
        sys.exit(0)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(CHROMA_PERSIST_DIR), exist_ok=True)
    
    # Start ChromaDB
    print(f"Starting ChromaDB on {CHROMA_HOST}:{CHROMA_PORT}")
    
    # Build the command
    cmd = [
        "chroma",
        "run",
        "--host", CHROMA_HOST,
        "--port", str(CHROMA_PORT),
        "--path", CHROMA_PERSIST_DIR
    ]
    
    # Start ChromaDB
    process = subprocess.Popen(cmd)
    
    # Wait for ChromaDB to start
    print("Waiting for ChromaDB to start...")
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(1)
        if is_port_in_use(CHROMA_PORT):
            # Verify ChromaDB is running with a health check
            try:
                response = requests.get(f"http://127.0.0.1:{CHROMA_PORT}{CHROMA_HEALTH_ENDPOINT}", timeout=5)
                if response.status_code == 200:
                    print("ChromaDB started successfully")
                    break
            except requests.RequestException:
                pass
        
        if i == max_attempts - 1:
            print("Failed to start ChromaDB")
            sys.exit(1)
    
    # Keep the script running to maintain the ChromaDB process
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down ChromaDB...")
        process.terminate()
        process.wait() 