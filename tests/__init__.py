"""Tests: python -m unittest discover tests (from the repository). They use the bundled wiki data only, never save files.

Many expectations are values read in game (character screen, skill levels, item tooltips), so a change that drifts
from the game fails here. Slow ones (the search engine check) can be skipped with CK_FAST_TESTS=1.
They import the package from src/, so they run without installing it.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(REPO, 'src') not in sys.path:
    sys.path.insert(0, os.path.join(REPO, 'src'))
