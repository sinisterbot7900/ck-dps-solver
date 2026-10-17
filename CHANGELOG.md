# Changelog

Notable changes to Core Keeper DPS Solver. Versions follow [semantic versioning](https://semver.org); each release's
section below becomes its GitHub release notes.

## [1.0.1] - 2026-10-17

### Added
- Mana strategy setting "Burst at full mana" (on by default): once mana runs out, wait for it to refill at the full
  regeneration rate, then burst again. It only waits when that gets more attacks, and not at the end of a fight. Off:
  attack whenever there is mana, as before. Applies to magic weapons and scepters.
- Default talents follow the mana strategy as well as the damage type (Magic: The best offense 4 and Mental defense 1
  with bursting, Mana recharge 4 without).
- Character tab: "Defaults for all skills" button.
- Results that were found with other settings than the current ones are flagged on the run bar ("settings changed");
  hovering lists the changes.

### Changed
- The run button and progress bar moved to the top of the window, on every tab. One button runs, and stops while
  running (Ctrl+R / Esc); the status is written on the bar.
- Results belong to their damage type: switching damage type clears them (they stay in the history), and picking an
  earlier run from the history switches to its damage type. The damage type is locked while a search runs.
- Character stats follow the search mode: every item uses the default skills and talents; your own items use the
  character's from the save.
- When searching every item, Druidra and Pyrdra souls only count once progression passes their bosses.
- Set conditions (Not hit, Kill stacks, Recently dodged, Burning, Recently mined, Adjacent to water) are on by default.
- Chest radius defaults to 50 tiles.
- Search tab: Output CSV moved into advanced settings, "Open results CSV" sits by the filter, and the history by the
  presets.

### Fixed
- Every-item searches gave the always-equipped pet no talents (Earie had none, so Summoning DPS was far too low). The
  pet now comes with its best talent, e.g. Earie with Drone Dominance against bosses and Breaking Skin otherwise.
- A Summoning search right after a Magic search counted scepters as reinforced twice.
- The Dynamic theme didn't follow the damage type for settings saved without a theme.

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

[1.0.1]: https://github.com/sinisterbot7900/ck-dps-solver/releases/tag/v1.0.1
[1.0.0]: https://github.com/sinisterbot7900/ck-dps-solver/releases/tag/v1.0.0
