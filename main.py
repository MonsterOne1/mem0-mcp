#!/usr/bin/env python
"""
Entry point for mem0-mcp server
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the server
if __name__ == "__main__":
    from src.server.main import main
    main()