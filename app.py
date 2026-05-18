"""
Entry point for Hugging Face Spaces deployment.
This file allows the app to be deployed on HF Spaces while maintaining
compatibility with local development.

Local use: python dashboard/app/main.py
HF Spaces: Automatically runs this app.py
"""

import sys
import os
from pathlib import Path

# Setup path
app_root = Path(__file__).parent
sys.path.insert(0, str(app_root))

# Import main app
from dashboard.app.main import main

if __name__ == "__main__":
    main()
