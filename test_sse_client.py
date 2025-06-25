#!/usr/bin/env python
"""
Test SSE client to debug ChatWise connection issues
"""
import asyncio
import aiohttp
import json
import sys
from datetime import datetime

async def test_sse_connection(base_url):
    """Test SSE connection flow similar to ChatWise"""
    print(f"\n[{datetime.now()}] Testing SSE connection to {base_url}")
    
    # First, check health endpoint
    async with aiohttp.ClientSession() as session:
        print(f"\n1. Checking health endpoint...")
        async with session.get(f"{base_url}/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✓ Health check passed: {data}")
            else:
                print(f"   ✗ Health check failed: {resp.status}")
                return
        
        # Check debug endpoint
        print(f"\n2. Checking debug endpoint...")
        async with session.get(f"{base_url}/debug/sse") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   ✓ Debug info: {json.dumps(data, indent=2)}")
            else:
                print(f"   ✗ Debug endpoint failed: {resp.status}")
        
        # Connect to SSE endpoint
        print(f"\n3. Connecting to SSE endpoint...")
        session_url = None
        
        try:
            async with session.get(f"{base_url}/sse", 
                                 headers={"Accept": "text/event-stream"}) as resp:
                print(f"   SSE Response status: {resp.status}")
                print(f"   SSE Response headers: {dict(resp.headers)}")
                
                if resp.status != 200:
                    print(f"   ✗ SSE connection failed: {resp.status}")
                    return
                
                # Read SSE events
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line:
                        print(f"   SSE line: {line}")
                        
                        # Parse SSE events
                        if line.startswith("event:"):
                            event_type = line[6:].strip()
                            print(f"   Event type: {event_type}")
                        elif line.startswith("data:"):
                            data = line[5:].strip()
                            print(f"   Event data: {data}")
                            
                            # Look for endpoint event
                            if event_type == "endpoint":
                                try:
                                    parsed = json.loads(data)
                                    session_url = parsed.get("endpoint")
                                    print(f"   ✓ Got session URL: {session_url}")
                                    break
                                except:
                                    pass
                    
                    # Timeout after 5 seconds
                    await asyncio.sleep(0.1)
                    
        except asyncio.TimeoutError:
            print("   ✗ SSE connection timeout")
        except Exception as e:
            print(f"   ✗ SSE connection error: {e}")
        
        # Try to send a message if we got a session URL
        if session_url:
            print(f"\n4. Testing message endpoint with session URL...")
            test_message = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }
            
            full_url = f"{base_url}{session_url}" if session_url.startswith("/") else session_url
            print(f"   Posting to: {full_url}")
            
            try:
                async with session.post(full_url, 
                                      json=test_message,
                                      headers={"Content-Type": "application/json"}) as resp:
                    print(f"   Response status: {resp.status}")
                    if resp.status == 200 or resp.status == 202:
                        print(f"   ✓ Message accepted!")
                    else:
                        body = await resp.text()
                        print(f"   ✗ Message failed: {body}")
            except Exception as e:
                print(f"   ✗ Message error: {e}")
        else:
            print("\n4. Could not test message endpoint - no session URL received")

if __name__ == "__main__":
    # Test locally or with deployed URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8080"  # Default local test
    
    print(f"Testing MCP SSE server at: {base_url}")
    asyncio.run(test_sse_connection(base_url))