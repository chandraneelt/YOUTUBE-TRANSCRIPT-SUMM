"""
Vercel serverless function for YouTube Comment Analyzer
"""
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Streamlit app
from app import *

# This is required for Vercel
def handler(request, response):
    return app