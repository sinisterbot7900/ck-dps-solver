# Changelog

Notable changes to Core Keeper DPS Solver. Versions follow [semantic versioning](https://semver.org); each release's
section below becomes its GitHub release notes.

## [1.0.0] - 2026-10-16

First public release.

### Added
- Desktop window: Search, Items, Settings, Character and Consumables tabs, color themes (including one per damage type
  and a Dynamic theme that follows it), presets and search history.
- Searches for Melee, Range, Magic and Summoning loadouts: weapon, armor, necklace, rings, offhand, and optionally
  lantern, bag and pet ("Try all" or "Best"), with set bonuses, talents, food and potions, mana, minions, poison and
  fight length.
- Reads Core Keeper saves: the items you own (inventory, storage chests and opened loot chests near your character),
  their upgrade levels, skills, talents, souls and permanent foods.
- Progression: limit items, food and potions to the biomes you've reached.
- Upgrade suggestions: the items you don't own yet that raise your DPS the most, with where to get them and drop chances.
- Loadout details: DPS over a fight, a character sheet with where every stat comes from, and pinning a loadout to compare.
- Cooking planner: the best dishes to cook from the ingredients you own.
- Command line: `ck-dps-solver search` with a JSON config, `ck-dps-solver defaults`.
- Default talents: the best legal build for each skill and damage type, found by trying every legal build.
- Windows app built and self-tested by GitHub Actions on each release.

[1.0.0]: https://github.com/sinisterbot7900/ck-dps-solver/releases/tag/v1.0.0
