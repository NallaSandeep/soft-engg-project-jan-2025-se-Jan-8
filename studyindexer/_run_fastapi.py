#!/usr/bin/env python3
"""
Simple standalone script to run the FastAPI server.
This script is designed to be run directly and will start the FastAPI server
without any dependencies on the service manager.
"""

import os
import sys
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Set the current working directory to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Print startup message
    print(f"Starting FastAPI server on {settings.HOST}:{settings.PORT}")
    
    # Run the FastAPI server
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    ) 