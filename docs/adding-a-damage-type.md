# Adding a damage type

A checklist for adding a new damage type (a weapon class with its own skill, talents and gear) to the solver. Work
through it in order; each step lists the files involved and what to check. File paths are relative to the package,
`src/ck_dps_solver/` (tests and tools are at the repository root). `<Type>` below is the new damage type's
name as the solver will spell it (e.g. in `Weapon.damage_type`, the GUI and `defaults.DAMAGE_TYPE`).

## 1. Research the mechanics first

Before writing code, collect and write down how the damage type works, and confirm the unclear parts in game.
Turn each confirmed reading into a test (`tests/`), so later changes can't break it.

- **Wiki data** (`data/wiki_data.json`, rebuilt by `python -m tools.wiki.build_data`):
  - the skill (`skills`): its per-level condition and its 8 talents in tree order
  - talents (`talents`): condition and value per point
  - weapons: which wiki weapon types carry the damage value (`<type>Damage` field) and any per-level cost
    (resource per attack) or other per-level weapon fields
  - conditions (`conditions`) whose `effect` mentions the damage type, and set bonuses (`sets`) that use them
- **What applies to it.** For every existing bonus, decide whether it applies to the new type:
  - general damage, crit, triple hit, boss damage, attack speed
  - the delivery: does the weapon hit at range or in melee (or both, per weapon)? Range/melee talents and
    "range damage"/"melee damage" (generic) follow the delivery; "physical" bonuses only apply to physical weapons
  - flat damage sources (thorns, fishing, mining) and set mechanics in the formula
- **Its own mechanics**: resources, timers, stacking, procs, durations, uptime over a fight. Note what's assumed
  vs. verified, and which values are per point, per level, or per stack.
- **Talent tree rules**: which builds are legal (`model/talents.py`) and the build players actually use
  (chosen in step 8b).

## 2. Wiki data and item building

- `tools/wiki/build_data.py`: add any new equipment fields to `EQUIPMENT_FIELDS` (e.g. a per-level resource cost);
  add a data module to `tools/wiki/fetch.py` `DATA_MODULES` if the type needs one. Rebuild the data.
- `model/item_stats.py`:
  - `WEAPON_TYPES` / `WEAPON_DAMAGE_TYPES`: the wiki weapon types and damage field for `<Type>`
  - `make_item`: the weapon's `delivery` and any new per-level weapon fields
  - `CONDITION_ATTRIBUTES`: map every wiki condition the type uses to a solver attribute. Map by the condition's
    `effect`: physical effects to `%_physical_*`, generic ones to the generic attributes. Remove anything newly
    mapped from `IGNORED_CONDITIONS`; add conditions that never affect damage there.
  - `scale_condition`: check the scale of new conditions (`descriptionIsAPercentage`, `showDecimal`; flat values
    with `showDecimal` are tenths)
  - `DAMAGE_TYPE_ATTRIBUTES`: the attributes only `<Type>` uses (decides `consider_for` of new items)
  - `considered_for` / `PHYSICAL_ONLY_ATTRIBUTES`: which items from other types the new type's search should include
    (by stats, so e.g. range attack speed items reach a range-delivery weapon of the new type). Set pieces only
    count when `set_helps` says their set has a bonus the type can use; otherwise useless set pieces (e.g. a
    mining-damage set for a non-melee type) tie with an empty slot and show up as "best".
- `model/weapon.py`: new weapon fields (with defaults so existing weapons don't change), and `delivery`.
- `model/item.py`: new attributes in the default `attributes` dict; flat ones in `FLAT_ATTRIBUTES` (rounded when
  reinforced).
- `tools/wiki/item_code.py` `entry_source`: write the new weapon fields into catalogue.py entries.
- `tools/verify.py` `check_items`: compare the new weapon fields too.

## 3. Character: attributes, talents, settings, set bonuses

`model/character.py`:

- `ACTIVE_EFFECTS_DICT`: every new attribute (same keys as `Item.attributes`), with a comment on how the formula uses it.
- `perk_to_label`: the skill's talent names in tree order (from the wiki skill data; the order of points in saves).
- `get_character_active_effects`: the skill level bonus, the talents, base values (e.g. a base resource pool), and
  which delivery/physical-only bonuses apply. Talents that are mechanics rather than plain bonuses go into the
  formula (step 4) instead.
- `SET_BONUSES`: the type's set bonuses (set ids are the wiki's). Situational ones get a setting.
- Settings: new situations as settings (bool, or a number like `Fight length`). Add their hover text to
  `SETTING_HELP` in `app/labels.py`.

## 4. The DPS formula

`engine/dps_utils.py` (`dps_core`, plain Python that numba compiles):

- Attribute index constants for new attributes; `PARAMS` and `params()` for weapon fields, talents and settings.
- The new branch: keep existing types' arithmetic unchanged; check with a random old-vs-new comparison (the
  results may differ only at rare rounding boundaries).
- numba rules: no calls to plain Python helpers (inline them), no dicts or strings, and initialize every variable
  on all paths before use.
- The optimistic bound (`params(..., optimistic=True)`, used by the skip-ahead): it must never be below the real
  DPS and must never decrease when any stat increases. Relax exactly the parts that break monotonicity.
- Time-dependent mechanics use the `Fight length` setting, like resources running out and buffs that take time to
  land; describe them in the module docstring.

## 5. Search filtering and the batch engine

`engine/dominance.py` (keeps searches fast; must stay exact):

- `UNUSED_ATTRIBUTES[<Type>]`: attributes the formula never reads for the type. Also add the new type's
  own attributes to the other types' lists.
- `EXACT_FOR_...` / `exact_attributes`: attributes where more can lower DPS for this type; items must be equal in
  them to dominate.
- `FORMULA_SETS_FOR`: formula sets that only matter for some types.
- Weapon dominance: skip it if weapons of the type differ in ways that aren't monotonic.
- `engine/upgrades.py` `can_help`: same exemptions.

`engine/batch_search.py`: nothing type-specific, but the kernel's compiled cache is cleared automatically when
`engine/dps_utils.py` or `model/` change (`_clear_stale_kernel_cache`); keep that list of files current.

Measure the search size (`loadouts` in the run log) and the time; if it's much bigger than the others, look for
items kept only because of attributes the type doesn't use, or sets wrongly protected (`relevant_groups`).

## 6. Items, pets, consumables

- **catalogue.py**: `python -m tools.wiki.item_code --level 20 --sync` to update existing entries (new attributes on
  old items), then `--insert <ids>` for the type's weapons and gear not in catalogue.py yet (list them from the wiki
  data: weapons with the damage field, gear with the type's attributes or sets).
- **Pets** (`model/pets.py`, catalogue.py `PETS`): check every pet's innate conditions and talents for the type's
  attributes; buff pets give their stats to the owner, attacking pets only their target effects. Update the
  hand-written catalogue.py pet entries. Compare pets on the top loadouts.
- **Consumables** (`model/consumables.py`): map food and potion conditions for the type (`CONDITION_ATTRIBUTES`,
  including separate "...FromPotion" conditions); defaults come from `default_keys` per type via
  `UNUSED_ATTRIBUTES`. Check the Consumables tab totals for the type.
- **Fixed items** (`defaults.py` `FIXED_ITEM_NAMES`): a lantern, bag and pet for the type.

## 7. Configuration and the app

- `defaults.py`: `perk_trees` / `skill_levels` defaults (the go-to build), `FIXED_ITEM_NAMES`, the
  damage types in `CONSUMABLES`, the `DAMAGE_TYPE` comment, and anything in `run_search` keyed on a type.
- `app/labels.py`: `DAMAGE_TYPES` (drives the damage type list, the always-equipped dropdowns and the consumables)
  and `SETTING_HELP`. Optionally a color theme for the type in `app/theme.py`.
- Everything else (Character tab talents, stat breakdown greying, upgrades, presets) follows from the above; check
  each in the GUI after a run.
- Search for hard-coded type names: `grep -rn "'Melee'\|'Range'" --include=*.py .` and the same for the most
  recently added type. Every hit should either handle the new type or not need to.

## 8. Verify

- `python -m tools.verify`: add `<Type>` to the damage types in `check_engine` and any new settings to its
  toggles. It checks items against the wiki, set ids, the batch engine against single loadouts, and the bound.
- A brute-force check that filtering doesn't change the best loadout: search small random catalogues with and
  without dominance and skip-ahead (`BOUNDS_DISABLED`) and compare.
- Old types unchanged: compare the old and new formula on random stats, and re-run a known search.
- Sanity checks in game: the top loadouts, DPS over fight length, and each assumption from step 1.
- Restart the GUI (a running GUI keeps the old code in memory).

## 8b. Choose the talent build

The search uses one talent tree per run, and gear choices depend on it (e.g. talents that turn a stat into damage
make gear with that stat worth much more). So pick the default build for the type:

1. **Enumerate builds**: every way to put the skill's points into its talents (e.g. 5 talents x 5 points = 56 builds
   of 8 talents). Don't filter by legality yet.
2. **Score them**: run one full catalogue search with a starting build, then score every build on its top 1,000
   loadouts (Character + `calculate_dps` per loadout; seconds, not a search per build). Do it for a short and a long
   `Fight length` if the type has time-dependent mechanics.
3. **Legal builds only**: check the ranking in game and flag which builds are legal (tree tiers, mutually
   exclusive talents; the rules are hard to derive from the data). Encode the rules in `model/talents.py`.
4. **Re-search the winner**: set the best legal build as the default in `defaults.py` `perk_trees` and run a full
   catalogue search with it, since gear picked for the starting build can underrate a build that wants other gear.
   If two builds are close, search both.
5. **Report the assumptions** the ranking depends on (settings such as full barrier or stacks, durations) so the
   user can decide how to treat them.

## 9. Document

- README: the type's section (how it works, assumptions) and its settings.
- Tests: the in-game readings that confirm the mechanics (`tests/`).
