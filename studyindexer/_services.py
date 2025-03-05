#!/usr/bin/env python3
"""
Simple script to manage ChromaDB and FastAPI services.
"""

import os
import sys
import time
import subprocess
import signal
import argparse

def is_port_in_use(port, host='127.0.0.1'):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def start_services():
    """Start all services"""
    print("Starting all services...")
    
    # Start ChromaDB
    print("Starting ChromaDB...")
    subprocess.Popen(["python", "start_chromadb.py"])
    print("ChromaDB starting process initiated")
    
    # Give ChromaDB a moment to start before starting FastAPI
    print("Waiting 10 seconds for ChromaDB to initialize...")
    time.sleep(10)
    
    # Start FastAPI
    print("Starting FastAPI...")
    subprocess.Popen(["python", "start_fastapi.py"])
    print("FastAPI starting process initiated")
    
    print("All services have been started. Use 'python services.py status' to check their status.")
    return True

def stop_services():
    """Stop all services"""
    print("Stopping all services...")
    
    # Stop FastAPI
    print("Stopping FastAPI...")
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq start_fastapi.py"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # Also try to kill by port
        if is_port_in_use(8081):
            subprocess.run(["for", "/f", "\"tokens=5\"", "%a", "in", "('netstat -aon ^| findstr :8081')", "do", "taskkill", "/F", "/PID", "%a"], shell=True)
    else:
        subprocess.run(["pkill", "-f", "start_fastapi.py"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # Also try to kill by port
        if is_port_in_use(8081):
            subprocess.run("kill $(lsof -t -i:8081)", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    print("FastAPI stop command issued")
    
    # Stop ChromaDB
    print("Stopping ChromaDB...")
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq start_chromadb.py"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # Also try to kill by port
        if is_port_in_use(8000):
            subprocess.run(["for", "/f", "\"tokens=5\"", "%a", "in", "('netstat -aon ^| findstr :8000')", "do", "taskkill", "/F", "/PID", "%a"], shell=True)
    else:
        subprocess.run(["pkill", "-f", "start_chromadb.py"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # Also try to kill by port
        if is_port_in_use(8000):
            subprocess.run("kill $(lsof -t -i:8000)", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    print("ChromaDB stop command issued")
    
    print("All stop commands have been issued. Use 'python services.py status' to check their status.")
    return True

def restart_services():
    """Restart all services"""
    print("Restarting all services...")
    stop_services()
    time.sleep(2)  # Give services time to fully stop
    start_services()
    return True

def check_service_status(service_name, port, health_endpoint=None):
    """Check status of a service"""
    if not is_port_in_use(port):
        return f"{service_name}: Not running"
    
    if health_endpoint:
        import requests
        try:
            response = requests.get(f"http://127.0.0.1:{port}{health_endpoint}", timeout=2)
            if response.status_code == 200:
                return f"{service_name}: Running (Healthy)"
            else:
                return f"{service_name}: Running (Unhealthy, status code: {response.status_code})"
        except requests.RequestException:
            return f"{service_name}: Running (Unhealthy, cannot connect to health endpoint)"
    
    return f"{service_name}: Running"

def status_services(continuous=False, interval=2):
    """Check status of all services"""
    if continuous:
        print("Monitoring services status (Ctrl+C to stop)...")
        try:
            while True:
                os.system('cls' if sys.platform == 'win32' else 'clear')
                print(f"Services Status (refreshing every {interval} seconds):")
                print("-" * 50)
                print(check_service_status("ChromaDB", 8000, "/api/v2/heartbeat"))
                print(check_service_status("FastAPI", 8081, "/api/health"))
                print("-" * 50)
                print("Press Ctrl+C to stop monitoring")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStatus monitoring stopped")
    else:
        print("Services Status:")
        print("-" * 50)
        print(check_service_status("ChromaDB", 8000, "/api/v2/heartbeat"))
        print(check_service_status("FastAPI", 8081, "/api/health"))
        print("-" * 50)
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Manage ChromaDB and FastAPI services")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], help="Action to perform")
    parser.add_argument("--monitor", "-m", action="store_true", help="Continuously monitor status (only with status action)")
    parser.add_argument("--interval", "-i", type=int, default=2, help="Refresh interval for continuous monitoring in seconds")
    args = parser.parse_args()
    
    if args.action == "start":
        start_services()
    elif args.action == "stop":
        stop_services()
    elif args.action == "restart":
        restart_services()
    elif args.action == "status":
        status_services(continuous=args.monitor, interval=args.interval)

if __name__ == "__main__":
    main() 