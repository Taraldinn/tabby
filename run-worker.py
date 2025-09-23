#!/usr/bin/env python3
"""
Worker script for Render deployment
Runs Django worker process with a simple HTTP health check server
"""

import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add the tabbycat directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tabbycat'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.core.management import execute_from_command_line


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Tabbycat Worker: Running\n')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found\n')
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass


def run_health_server():
    """Run simple HTTP server for Render port detection"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Worker health check server running on port {port}")
    server.serve_forever()


def run_worker():
    """Run Django worker process"""
    print("Starting Tabbycat worker process...")
    # Small delay to let HTTP server start first
    time.sleep(2)
    
    # Run the Django worker
    execute_from_command_line([
        'manage.py', 
        'runworker', 
        'notifications', 
        'adjallocation', 
        'venues'
    ])


if __name__ == '__main__':
    print("="*60)
    print("TABBYCAT WORKER STARTING")
    print("This service runs background tasks")
    print("="*60)
    
    # Start HTTP server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Run worker in main thread
    run_worker()