"""Summoner loadouts: a summon tome for the minions plus a scepter to hold and attack with.

Every scepter curses what it hits (minions deal 40% more damage to cursed targets, for 8 sec, refreshed by each hit),
so a summoner summons with the tome, then switches to a scepter. The loadout's weapon is a SummonerKit of the two:
its DPS is the minions' plus the scepter's own (see engine/dps_utils.py). Without a scepter, the tome alone.
"""
from ck_dps_solver.model import SummonerKit


def summoner_kits(weapons):
    """Every tome + scepter pair from a list of tomes and scepters (other weapons are dropped). Tomes alone if no scepter."""
    tomes = [w for w in weapons if w.damage_type == 'Summoning' and not isinstance(w, SummonerKit)]
    scepters = [w for w in weapons if getattr(w, 'curses', False) and w.damage_type == 'Magic']
    kits = [w for w in weapons if isinstance(w, SummonerKit)]
    return kits + [SummonerKit(tome, scepter) for tome in tomes for scepter in (scepters or [None])]
