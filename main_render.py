#!/usr/bin/env python
"""
Main entry point for Render deployment
Uses the fixed implementation to avoid module import issues
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Run the fixed implementation
    script_path = os.path.join(os.path.dirname(__file__), 'main_render_fixed.py')
    subprocess.run([sys.executable, script_path] + sys.argv[1:])