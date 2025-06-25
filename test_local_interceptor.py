#!/usr/bin/env python
"""Test the interceptor locally"""
import subprocess
import time
import requests
import json
import sys

def test_interceptor():
    """Test stale session interceptor"""
    
    # Start the server
    print("Starting server...")
    server = subprocess.Popen(
        [sys.executable, "main_render.py", "--port", "8888"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test stale session
        stale_session_id = "467db479-421a-41d2-9ff4-a7ad29678bb6"
        url = f"http://localhost:8888/messages/?session_id={stale_session_id}"
        
        print(f"\nTesting URL: {url}")
        
        response = requests.post(
            url,
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {json.dumps(response.json(), indent=2) if response.content else 'No content'}")
        
        if response.status_code == 410:
            print("\n✅ SUCCESS: Interceptor is working!")
        else:
            print(f"\n❌ FAILED: Expected 410, got {response.status_code}")
            
    finally:
        # Stop server
        server.terminate()
        server.wait()
        print("\nServer stopped")

if __name__ == "__main__":
    test_interceptor()