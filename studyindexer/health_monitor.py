#!/usr/bin/env python3
"""
StudyIndexer Health Monitor
--------------------------
Continuously monitors the health of all StudyIndexer services.
"""
import time
import logging
import argparse
import requests
import subprocess
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("health-monitor")

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

# Service definitions with environment variable support
SERVICES = {
    "chromadb": {
        "name": "ChromaDB",
        "health_url": f"http://localhost:{get_env('CHROMA_PORT', '8000')}{get_env('CHROMA_HEALTH_ENDPOINT', '/api/v1/heartbeat')}",
        "health_check": lambda: requests.get(f"http://localhost:{get_env('CHROMA_PORT', '8000')}{get_env('CHROMA_HEALTH_ENDPOINT', '/api/v1/heartbeat')}", timeout=get_env_int("HEALTH_CHECK_TIMEOUT", 10)).status_code == 200,
        "required": get_env("CHROMA_REQUIRED", "true").lower() == "true"
    },
    "fastapi": {
        "name": "FastAPI Server",
        "health_url": f"http://localhost:{get_env('PORT', '8080')}{get_env('FASTAPI_HEALTH_ENDPOINT', '/health')}",
        "health_check": lambda: requests.get(f"http://localhost:{get_env('PORT', '8080')}{get_env('FASTAPI_HEALTH_ENDPOINT', '/health')}", timeout=get_env_int("HEALTH_CHECK_TIMEOUT", 10)).status_code == 200,
        "required": get_env("FASTAPI_REQUIRED", "true").lower() == "true"
    }
}

def check_service_health(service_name):
    """Check the health of a specific service"""
    if service_name not in SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return False
    
    service = SERVICES[service_name]
    
    try:
        if 'health_check' in service:
            is_healthy = service['health_check']()
            return is_healthy
        else:
            logger.warning(f"No health check defined for {service['name']}")
            return True  # Assume healthy if no check is defined
    except Exception as e:
        logger.error(f"Health check failed for {service['name']}: {str(e)}")
        return False

def check_all_health():
    """Check health of all services and return results"""
    results = {}
    all_healthy = True
    
    # Get service order from environment or use default
    service_order = get_env_list("SERVICE_CHECK_ORDER", list(SERVICES.keys()))
    
    for service_name in service_order:
        if service_name not in SERVICES:
            logger.warning(f"Unknown service in check order: {service_name}")
            continue
            
        service = SERVICES[service_name]
        is_healthy = check_service_health(service_name)
        results[service_name] = {
            "name": service["name"],
            "healthy": is_healthy,
            "required": service.get("required", False)
        }
        
        if not is_healthy and service.get("required", False):
            all_healthy = False
    
    return all_healthy, results

def print_health_status(results):
    """Print the health status in a formatted way"""
    print("\n" + "=" * 50)
    print(f"HEALTH STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    for service_name, info in results.items():
        status = "✅ HEALTHY" if info["healthy"] else "❌ UNHEALTHY"
        required = "[REQUIRED]" if info["required"] else "[OPTIONAL]"
        print(f"{info['name']} {required}: {status}")
    
    print("=" * 50 + "\n")

def monitor_health(interval=60, output_format="text"):
    """Continuously monitor the health of all services"""
    logger.info(f"Starting health monitoring (interval: {interval}s)")
    
    try:
        while True:
            all_healthy, results = check_all_health()
            
            if output_format == "text":
                print_health_status(results)
            elif output_format == "log":
                status_str = "HEALTHY" if all_healthy else "UNHEALTHY"
                logger.info(f"System status: {status_str}")
                for service_name, info in results.items():
                    status = "HEALTHY" if info["healthy"] else "UNHEALTHY"
                    logger.info(f"{info['name']}: {status}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Health monitoring stopped by user")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StudyIndexer Health Monitor")
    parser.add_argument("--interval", type=int, default=get_env_int("HEALTH_CHECK_INTERVAL", 60), 
                        help=f"Check interval in seconds (default: {get_env_int('HEALTH_CHECK_INTERVAL', 60)})")
    parser.add_argument("--format", choices=["text", "log"], default=get_env("HEALTH_CHECK_FORMAT", "text"), 
                        help=f"Output format (default: {get_env('HEALTH_CHECK_FORMAT', 'text')})")
    
    args = parser.parse_args()
    
    # Change to the script directory
    os.chdir(Path(__file__).parent)
    
    monitor_health(interval=args.interval, output_format=args.format)

if __name__ == "__main__":
    main() 