#!/usr/bin/env python
"""
Legacy compatibility wrapper for main_render.py
Redirects to the new unified server implementation
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the new server in full mode
if __name__ == "__main__":
    # Force full mode for Render deployment
    sys.argv.extend(['--mode', 'full'])
    
    # Check if we're on Render and need to use their PORT
    if 'RENDER' in os.environ and '--port' not in sys.argv:
        port = os.environ.get('PORT', '10000')
        sys.argv.extend(['--port', port])
    
    from src.server.main import main
    main()