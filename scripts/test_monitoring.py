#!/usr/bin/env python3
"""
Test script to verify the monitoring solution works correctly.
Run this after starting both server and agent.
"""

import json
import time
import requests
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_collector_health():
    """Test collector server health endpoint."""
    try:
        response = requests.get('https://localhost:8443/health', verify=False, timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

def test_hosts_endpoint():
    """Test the hosts listing endpoint."""
    try:
        headers = {'Authorization': 'Bearer SECRET'}
        response = requests.get('https://localhost:8443/api/hosts', 
                              headers=headers, verify=False, timeout=10)
        print(f"Hosts endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Monitored hosts: {data.get('total_hosts', 0)}")
            for hostname, info in data.get('hosts', {}).items():
                print(f"  {hostname}: CPU {info.get('cpu_percent', 'N/A')}%, "
                      f"Memory {info.get('memory_percent', 'N/A')}%")
            return True
    except Exception as e:
        print(f"Hosts endpoint failed: {e}")
    return False

def main():
    """Run monitoring tests."""
    print("Testing monitoring solution...")
    print("=" * 50)
    
    # Wait a moment for services to start
    print("Waiting for services to initialize...")
    time.sleep(5)
    
    # Test health endpoint
    if test_collector_health():
        print("✓ Collector server is healthy")
    else:
        print("✗ Collector server health check failed")
        return
    
    # Wait for agent to send some data
    print("Waiting for agent to send metrics...")
    time.sleep(20)
    
    # Test hosts endpoint
    if test_hosts_endpoint():
        print("✓ Hosts endpoint working")
    else:
        print("✗ Hosts endpoint failed")
    
    print("=" * 50)
    print("Test completed. Check the data/ directory for metric files.")

if __name__ == '__main__':
    main()

