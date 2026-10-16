"""Developer tools: python -m tools.verify, python -m tools.wiki.<tool> (run from the repository).

They import the package from src/, so they work without installing it.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.join(REPO, 'src', 'ck_dps_solver')
if os.path.join(REPO, 'src') not in sys.path:
    sys.path.insert(0, os.path.join(REPO, 'src'))
