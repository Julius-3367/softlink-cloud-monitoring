#!/usr/bin/env python3
"""
Cloud Monitoring Solution - Production Ready

Usage:
  Server Mode: python monitor.py --server [--port 8443] [--host 0.0.0.0]
  Agent Mode:  python monitor.py --agent --collector https://server:8443/api/metrics --token 3367

  Agent can also use config file: python monitor.py --agent --config agent_config.json

Dependencies: pip install psutil requests flask

The server runs with TLS enabled (self-signed cert generated automatically).
The agent collects system metrics and sends them to the collector every 15 seconds.
"""

import argparse
import json
import logging
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict
import socket

# Third-party imports
try:
    import psutil
    import requests
    from flask import Flask, request, jsonify
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install psutil requests flask")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable urllib3 warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ====================================================================
# MONITORING AGENT
# ====================================================================

class MonitoringAgent:
    """Production-ready monitoring agent that collects system metrics."""

    def __init__(self, collector_url: str, auth_token: str, interval: int = 15):
        self.collector_url = collector_url
        self.auth_token = auth_token
        self.interval = interval
        self.hostname = socket.gethostname()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json',
            'User-Agent': f'MonitoringAgent/1.0 ({self.hostname})'
        })
        self.running = False

    def collect_metrics(self) -> Dict:
        metrics = {
            "hostname": self.hostname,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict()
        }
        return metrics

    def push_metrics(self):
        metrics = self.collect_metrics()
        try:
            response = self.session.post(self.collector_url, json=metrics, verify=False)
            if response.status_code != 200:
                logger.warning(f"Failed to push metrics: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error pushing metrics: {e}")

    def run(self):
        self.running = True
        logger.info(f"Starting MonitoringAgent, pushing metrics to {self.collector_url} every {self.interval}s")
        while self.running:
            self.push_metrics()
            time.sleep(self.interval)

    def stop(self):
        self.running = False

# ====================================================================
# COLLECTOR SERVER
# ====================================================================

class CollectorServer:
    """Production-ready metrics collector server."""

    def __init__(self, host: str = '0.0.0.0', port: int = 8443, auth_token: str = '3367'):
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)

        # Create Flask app
        self.app = Flask(__name__)
        self.setup_routes()

        # Generate self-signed certificate if not exists
        self.cert_file = 'server.crt'
        self.key_file = 'server.key'
        self.ensure_ssl_cert()

    def ensure_ssl_cert(self):
        if not Path(self.cert_file).exists() or not Path(self.key_file).exists():
            logger.info("Generating self-signed certificate...")
            os.system(f"openssl req -x509 -newkey rsa:4096 -nodes -keyout {self.key_file} -out {self.cert_file} -days 365 -subj '/CN=localhost'")

    def setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                "data_dir": str(self.data_dir),
                "files_count": len(list(self.data_dir.glob('*'))),
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        @self.app.route('/api/metrics', methods=['POST'])
        def receive_metrics():
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token != self.auth_token:
                return jsonify({"error": "Unauthorized"}), 401
            data = request.json
            filename = self.data_dir / f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return jsonify({"status": "ok"}), 200

    def run(self):
        logger.info(f"Starting CollectorServer on https://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, ssl_context=(self.cert_file, self.key_file))

# ====================================================================
# CONFIGURATION AND MAIN
# ====================================================================

def load_agent_config(path: str) -> Dict:
    with open(path, 'r') as f:
        return json.load(f)

def create_sample_config():
    config = {
        "collector_url": "https://localhost:8443/api/metrics",
        "auth_token": "3367",
        "interval": 15,
        "hostname_override": None
    }
    with open('agent_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    logger.info("Created sample configuration file: agent_config.json")

def main():
    parser = argparse.ArgumentParser(description='Cloud Monitoring Solution')
    parser.add_argument('--server', action='store_true', help='Run as collector server')
    parser.add_argument('--agent', action='store_true', help='Run as monitoring agent')
    parser.add_argument('--collector', type=str, help='Collector URL for agent mode')
    parser.add_argument('--token', type=str, help='Authentication token')
    parser.add_argument('--config', type=str, help='Configuration file for agent')
    parser.add_argument('--interval', type=int, default=15, help='Push interval in seconds')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server bind address')
    parser.add_argument('--port', type=int, default=8443, help='Server port')
    parser.add_argument('--create-config', action='store_true', help='Create sample config file')

    args = parser.parse_args()

    if args.create_config:
        create_sample_config()
        return

    if args.server:
        auth_token = args.token or '3367'
        server = CollectorServer(host=args.host, port=args.port, auth_token=auth_token)
        server.run()
    elif args.agent:
        if args.config:
            config = load_agent_config(args.config)
            collector_url = config.get('collector_url')
            auth_token = config.get('auth_token')
            interval = config.get('interval', 15)
        else:
            collector_url = args.collector
            auth_token = args.token or '3367'
            interval = args.interval

        if not collector_url or not auth_token:
            logger.error("Agent requires --collector and --token arguments or --config file")
            sys.exit(1)

        agent = MonitoringAgent(collector_url, auth_token, interval)
        try:
            agent.run()
        except KeyboardInterrupt:
            logger.info("Shutting down agent...")
            agent.stop()
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python monitor.py --server --token 3367")
        print("  python monitor.py --agent --collector https://server:8443/api/metrics --token 3367")
        print("  python monitor.py --create-config")

if __name__ == '__main__':
    main()

