#!/usr/bin/env python
"""
Simplified entry point for mem0-mcp server
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.server.main import main

if __name__ == "__main__":
    main()