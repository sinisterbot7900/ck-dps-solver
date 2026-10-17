"""Core Keeper DPS Solver: finds the gear loadout with the highest damage per second for a Core Keeper character.

Subpackages: model (game rules and data), engine (DPS formula and search), saves (save files), app (the window).
"""
from ck_dps_solver import paths # First: sets numba's cache folder in the packaged app

__version__ = '1.0.1'
