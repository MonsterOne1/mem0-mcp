#!/usr/bin/env python
"""
Legacy compatibility wrapper for main.py
Redirects to the new unified server implementation
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the new server in basic mode
if __name__ == "__main__":
    # Force basic mode for compatibility
    sys.argv.extend(['--mode', 'basic'])
    
    from src.server.main import main
    main()