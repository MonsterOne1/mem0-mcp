#!/usr/bin/env python
"""Test script to verify stale session interception"""
import requests
import json
import sys

def test_stale_session(base_url):
    """Test that stale session is properly intercepted"""
    
    # The known stale session ID
    stale_session_id = "467db479-421a-41d2-9ff4-a7ad29678bb6"
    
    # Test URL
    test_url = f"{base_url}/messages/?session_id={stale_session_id}"
    
    print(f"\nTesting stale session interception...")
    print(f"URL: {test_url}")
    
    # Test message
    test_message = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    try:
        response = requests.post(
            test_url,
            json=test_message,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 410:
            print("\n✅ SUCCESS: Stale session was intercepted!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"\n❌ FAILED: Expected 410, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    test_stale_session(base_url)