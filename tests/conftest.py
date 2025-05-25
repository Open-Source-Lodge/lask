"""
Configure pytest for the lask test suite.
"""

import sys
from pathlib import Path

# Add the project root to the Python path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
