#coding=utf-8
"""
WebSocket startup script - Launch erniebot service in WebGL/WebSocket mode
"""

import os
import sys
import subprocess
import webbrowser
import time
import http.server
import socketserver
import threading
from pathlib import Path

# Get current script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))
# Project root directory
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Import configuration
from config_integration import HOST, PORT, DEBUG

def start_web_server(web_dir, port=8000):
    """Start a simple web server to serve WebGL content"""
    os.chdir(web_dir)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add necessary CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            http.server.SimpleHTTPRequestHandler.end_headers(self)
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Web server started on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Web server stopped")
        finally:
            httpd.server_close()

def start_erniebot_server():
    """Start erniebot server (WebSocket mode)"""
    # Set WEB_MODE environment variable
    env = os.environ.copy()
    env["WEB_MODE"] = "True"
    
    # Start erniebot service
    process = subprocess.Popen(
        [sys.executable, os.path.join(SCRIPT_DIR, "main.py")],
        env=env,
        cwd=ROOT_DIR
    )
    
    return process

def main():
    """Main function: Start Web server and erniebot service"""
    print("Starting erniebot service in WebGL mode...")
    
    # Check if web directory exists
    web_dir = os.path.join(ROOT_DIR, "web")
    if not os.path.exists(web_dir):
        print(f"Error: Web directory {web_dir} does not exist")
        return
    
    # Check if index.html exists
    if not os.path.exists(os.path.join(web_dir, "index.html")):
        print(f"Error: index.html not found in web directory")
        return
    
    # Check if websockets library is installed
    try:
        import websockets
    except ImportError:
        print("Installing required websockets library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
        print("websockets library installation complete")
    
    # Start Web server (in a new thread)
    web_port = 8000
    web_thread = threading.Thread(
        target=start_web_server,
        args=(web_dir, web_port),
        daemon=True
    )
    web_thread.start()
    
    # Set WebSocket mode environment variable
    os.environ["WEB_MODE"] = "True"
    
    # Start erniebot server
    erniebot_process = start_erniebot_server()
    
    try:
        # Increase wait time for server startup
        print("Waiting for server to start...")
        time.sleep(5)  # Increased to 5 seconds
        
        # Open Web browser
        web_url = f"http://localhost:{web_port}"
        print(f"Opening Web browser: {web_url}")
        webbrowser.open(web_url)
        
        print("\nService started! WebGL client is running in browser")
        print(f"erniebot WebSocket server running at: {HOST}:{PORT}")
        print(f"Web server running at: http://localhost:{web_port}")
        print("Press Ctrl+C to stop service")
        
        # Wait for main process to end
        erniebot_process.wait()
    except KeyboardInterrupt:
        print("\nUser interrupt, closing services...")
    finally:
        # Ensure proper shutdown of erniebot process
        if erniebot_process and erniebot_process.poll() is None:
            erniebot_process.terminate()
            try:
                erniebot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                erniebot_process.kill()
        
        print("Service closed")

if __name__ == "__main__":
    main() 