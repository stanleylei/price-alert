#!/usr/bin/env python3
"""
Health check module for the price alert service.
Provides HTTP endpoint for container health monitoring.
"""

import asyncio
import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HealthStatus:
    """Singleton class to track service health status"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize health status tracking"""
        self.service_started = datetime.now()
        self.last_check = datetime.now()
        self.scrapers_status = {}
        self.is_healthy = True
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.errors = []
        
    def update_scraper_status(self, scraper_name: str, status: str, error: Optional[str] = None):
        """Update the status of a specific scraper"""
        self.scrapers_status[scraper_name] = {
            "status": status,
            "last_run": datetime.now().isoformat(),
            "error": error
        }
        
        if status == "success":
            self.successful_runs += 1
        elif status == "failure":
            self.failed_runs += 1
            if error:
                self.errors.append({
                    "scraper": scraper_name,
                    "error": error,
                    "timestamp": datetime.now().isoformat()
                })
                # Keep only last 10 errors
                self.errors = self.errors[-10:]
        
        self.total_runs += 1
        self.last_check = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        uptime_seconds = (datetime.now() - self.service_started).total_seconds()
        
        return {
            "status": "healthy" if self.is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime_seconds),
            "uptime_human": self._format_uptime(uptime_seconds),
            "last_check": self.last_check.isoformat(),
            "statistics": {
                "total_runs": self.total_runs,
                "successful_runs": self.successful_runs,
                "failed_runs": self.failed_runs,
                "success_rate": (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0
            },
            "scrapers": self.scrapers_status,
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "< 1m"


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health check endpoint"""
    
    def log_message(self, format, *args):
        """Override to reduce verbosity of HTTP logs"""
        if args[1] != '200':
            logger.info(f"Health check: {args[0]} - {args[1]}")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self._send_health_status()
        elif self.path == '/ready':
            self._send_ready_status()
        elif self.path == '/metrics':
            self._send_metrics()
        else:
            self.send_error(404, "Not Found")
    
    def _send_health_status(self):
        """Send health status response"""
        health = HealthStatus()
        status = health.get_status()
        
        self.send_response(200 if health.is_healthy else 503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status, indent=2).encode())
    
    def _send_ready_status(self):
        """Send readiness status response"""
        health = HealthStatus()
        is_ready = health.total_runs > 0  # Ready after at least one run
        
        self.send_response(200 if is_ready else 503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "ready": is_ready,
            "message": "Service is ready" if is_ready else "Service is starting up"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _send_metrics(self):
        """Send Prometheus-style metrics"""
        health = HealthStatus()
        status = health.get_status()
        
        metrics = []
        metrics.append(f"# HELP price_alert_up Service up status")
        metrics.append(f"# TYPE price_alert_up gauge")
        metrics.append(f"price_alert_up {{}} {1 if health.is_healthy else 0}")
        
        metrics.append(f"# HELP price_alert_uptime_seconds Service uptime in seconds")
        metrics.append(f"# TYPE price_alert_uptime_seconds counter")
        metrics.append(f"price_alert_uptime_seconds {{}} {status['uptime_seconds']}")
        
        metrics.append(f"# HELP price_alert_total_runs Total number of scraper runs")
        metrics.append(f"# TYPE price_alert_total_runs counter")
        metrics.append(f"price_alert_total_runs {{}} {status['statistics']['total_runs']}")
        
        metrics.append(f"# HELP price_alert_successful_runs Total successful scraper runs")
        metrics.append(f"# TYPE price_alert_successful_runs counter")
        metrics.append(f"price_alert_successful_runs {{}} {status['statistics']['successful_runs']}")
        
        metrics.append(f"# HELP price_alert_failed_runs Total failed scraper runs")
        metrics.append(f"# TYPE price_alert_failed_runs counter")
        metrics.append(f"price_alert_failed_runs {{}} {status['statistics']['failed_runs']}")
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write('\n'.join(metrics).encode())


class HealthCheckServer:
    """Health check HTTP server"""
    
    def __init__(self, port: int = 8080):
        """Initialize health check server"""
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self):
        """Start the health check server in a background thread"""
        self.server = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info(f"Health check server started on port {self.port}")
        logger.info(f"Health endpoints available:")
        logger.info(f"  - http://localhost:{self.port}/health - Full health status")
        logger.info(f"  - http://localhost:{self.port}/ready - Readiness check")
        logger.info(f"  - http://localhost:{self.port}/metrics - Prometheus metrics")
    
    def _run_server(self):
        """Run the server (called in background thread)"""
        try:
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"Health check server error: {str(e)}")
    
    def stop(self):
        """Stop the health check server"""
        if self.server:
            self.server.shutdown()
            logger.info("Health check server stopped")


def start_health_check_server(port: int = 8080) -> HealthCheckServer:
    """
    Start the health check server.
    
    Args:
        port: Port to listen on
        
    Returns:
        HealthCheckServer instance
    """
    server = HealthCheckServer(port)
    server.start()
    return server


if __name__ == "__main__":
    # Test the health check server
    logging.basicConfig(level=logging.INFO)
    
    server = start_health_check_server(8080)
    
    # Simulate some scraper runs
    health = HealthStatus()
    health.update_scraper_status("power_to_choose", "success")
    health.update_scraper_status("villa_del_arco", "failure", "Connection timeout")
    health.update_scraper_status("alaska_award_ticket", "success")
    
    print("Health check server running on http://localhost:8080/health")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("\nServer stopped")