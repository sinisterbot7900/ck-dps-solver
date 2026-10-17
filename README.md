# Core Keeper DPS Solver

Finds the gear loadout with the highest damage per second for your Core Keeper character. It tries every
combination of weapon, armor, necklace, rings, offhand (and optionally lantern, bag and pet), using your skills,
talents, food and potions, and ranks them by DPS.

- **Melee, Range, Magic and Summoning**, each with its own talents, sets and mechanics (mana, minions, poison,
  stacks, fight length).
- **Reads your saves**: search only the items you own (inventory and nearby chests), with their real upgrade
  levels, skills, talents, souls and permanent foods.
- **Upgrade suggestions**: the items you don't own yet that would raise your DPS the most, and where to get them.
- **Progression aware**: limit items, food and potions to the biomes you've reached.
- **Breakdowns**: DPS over a fight, a character sheet and where every stat comes from; pin a loadout to compare.
- **Cooking planner**: the best dishes you can cook from the ingredients you own.

## Download (Windows)

Download the latest `CK DPS Solver` zip from [Releases](https://github.com/sinisterbot7900/ck-dps-solver/releases), unzip
it anywhere and run `CK DPS Solver.exe`. Keep the whole folder together. Windows may warn that the app is from an
unknown publisher (it isn't code-signed): click "More info", then "Run anyway".

The first search compiles the DPS code, which takes a minute or so; later searches reuse it. Settings, presets and
results are kept in `%LOCALAPPDATA%\ck-dps-solver`.

## Run from source

Needs Python 3.13 or newer (developed on 3.14). From a clone of this repository:

```
pip install .
ck-dps-solver
```

`ck-dps-solver` (or `python -m ck_dps_solver`) opens the window; `ck-dps-solver-gui` does the same without a console
window. Settings, presets and results are kept in `%LOCALAPPDATA%\ck-dps-solver` (on Linux and macOS,
`~/.local/share/ck-dps-solver`); set `CK_DPS_SOLVER_HOME` to use another folder.

## Using it

1. **Damage type**: pick it at the top of the window.
2. **Items tab**: to search only items you own, choose "Only items I own", pick your character and world (your
   Core Keeper save folder is found automatically) and click Load. Load also reads your skills, talents, souls and
   permanent foods. Otherwise choose how far you've progressed ("Up to" a biome) to search every item from there.
3. **Settings, Character and Consumables tabs**: fight conditions (boss fight, fight length, set conditions), skill
   levels and talents, and the food and potions you use. The default talents are the best legal build for each damage
   type (level 100, assuming a full magic barrier); talents left at the defaults follow the damage type you pick.
4. **Run** with the ▶ button at the top of the window (Ctrl+R; it turns into a stop button while searching, or press Esc).
   Click a loadout on the Search tab for its breakdown; the Upgrades tab lists what to get next.

The game only writes its save files now and then: for up-to-date items, quit to the menu before clicking Load.

## How it works

Item stats, set bonuses, talents, food and drop sources come from the
[Core Keeper Fandom wiki](https://core-keeper.fandom.com)'s data modules, bundled in the package (`data/wiki_data.json`). Where the
wiki is missing or out of date (for example the experience curves after update 1.3.0.1), values were checked in game,
and the tests hold those readings. What's still assumed, and how you can test it, is in
[docs/unknowns-and-assumptions.md](docs/unknowns-and-assumptions.md).

### Settings
Several set bonuses and item effects only count when their setting is on (Settings tab):
- "Max health": Solarite and Galaxite sets
- "Low health": Octarine set (assumes 75% missing health) and the Desperate fighter talent
- "Standing still": Hunter set, Chime Necklace
- "Range stacks": Dreamer set
- "Not hit": Pandorium set
- "Kill stacks": Scarlet set
- "Recently dodged": Assassin set
- "Burning": Welder set
- "Recently mined": Carapace set
- "Vs boss": all damage against bosses (Golem set, Spine Ring, Strength of the Ancients, ...). Turn off for regular enemies
- "Adjacent to water": Swamp Mage set (magic)
- "Full barrier": magic barrier counts for The best offense, Mage Low set, Arcane transfusion and the Warped set (magic)
- "Druidra soul", "Permanent max health": max health for Summoning (Heartbound horde)
- "Fight length": seconds of nonstop attacking, starting at full mana with no poison on the target.
  Poison you apply is a chance per hit that lasts 15 seconds (reapplying resets it), so Potent poison,
  Druidra's Ring and the Ivy set count for the share of the fight the target is poisoned. Short fights favor
  burst, long fights favor poison and mana regen. An attacking pet's poison counts as always up (except for Ivy).

### Magic
Staffs, scepters and beam staffs hit at range, so range talents and range attack speed apply (Rapid shots, Keeping
momentum, Weakness detection...), but not physical range damage (Range skill, Pheromoth, fishing). The Zealot's
Scimitar hits in melee and uses the melee talents the same way. Mana follows the wiki: 100 max mana plus items,
10 mana per second plus items, halved for 1 second after each attack. When a weapon spends mana faster than you
regenerate it, you attack at full speed until mana runs out, then only as fast as regeneration allows, so DPS depends
on "Fight length". Fully charged and the Mage Mid set count for your average remaining mana. Arcane frenzy
(6 seconds) and the Soaring set (assumed 3 seconds) are buffs on critical hits.

### Summoning
A summoner has two weapons: a summon tome (its minions keep fighting) and a scepter you hold and attack with. Every
scepter's hits curse the target, so minions deal 40% more damage to it ("Cursed target" setting). DPS is the minions'
plus the scepter's own magic damage; minions reserve mana, so the scepter gets what's left, and the best number of
minions to summon is chosen. Gear is picked for the minions (minion stats, max mana, magic damage, max health): the
scepter's damage counts, but gear that only helps the scepter isn't searched. Minions only get effects that say
minion: minion damage, attack speed, crit chance and damage, boss damage, the Summoning skill and talents, and
Trickle down arcana / the Grim set's share of your magic damage bonus. You get one minion plus "max minion" gear,
sets and pets, as long as their reserved mana fits in your max mana. Heartbound horde uses your max health (base 100,
Vitality, Maxed out!, gear, permanent foods, the Druidra soul and well fed). Attack cycles come from the wiki's tome
pages; orbiting minions are assumed to stay in contact with the target. Assumed: minions' base critical hit damage
is +50% like yours. The Tome of Breach isn't searched (its pickaxe's attack rate isn't known).

### Explosives
Explosives isn't in the window (grenades alone are far weaker than every other damage type), but
`ck-dps-solver search --damage-type Explosives` searches grenades (one throw every 1.5 seconds).
Explosions only get explosives bonuses (the Explosives skill, Explosives engineer, explosives damage gear, the Sulfur
set): they can't crit or triple hit, and generic and boss damage bonuses don't apply. Mortars and zookas (range
weapons) explode too: their range hit gets range bonuses and their explosion only explosives bonuses.

### Food and potions
The Consumables tab lists food and potions, chosen separately per damage type (Defaults picks the strongest source
for each effect). Dishes with a golden ingredient are rare (+25% on the ingredients' cooked effects, checked in game);
with both ingredients golden, x1.15 more. The same effect from two sources only counts once, the strongest, as in
the game's data; different effects stack. The Totals panel shows what counts. "Pick from: What I own" uses only the
food and potions in your saves, including the exact dishes you've cooked.

**What to cook** (bottom of the Consumables tab): with your character loaded and a search run, Plan scores every dish
the ingredients in your saves make on the loadout selected on the Search tab. Gain %: on top of the food that search
used; Alone %: with no other food. Epic dishes need luck, so they aren't planned.

### Progression
Choosing "Up to" a biome loads items, food and potions from that biome and every one before it, at their base level.
Items only a boss gives count from the next biome, once the boss is beaten (e.g. the Scarab set from Ra-Akar), and
random boss drops no earlier than the Forgotten Ruins: before the Cloaked Merchant sells summoning idols, a boss can't
be fought again. With your save loaded, progression only limits the upgrade suggestions; the items you own are always
searched.

### Upgrade suggestions
With owned items and a progression chosen, the run also tries every item up to that biome that you don't own (at its
base level, as found), one at a time, plus the missing pieces of each set together. The Upgrades tab ranks them by
how much they raise your best DPS and says where to get them (crafting, drops, chests, fishing, merchants), with drop
chances from the wiki. Seasonal items are marked.

## Command line

```
ck-dps-solver search --damage-type Magic --top 1000
ck-dps-solver search --character "<save folder>/saves/0.json" --world "<save folder>/worlds/0.world.gzip"
ck-dps-solver defaults > my-config.json
ck-dps-solver search --config my-config.json
```

`search` runs a search in the terminal and writes the best loadouts to a CSV (by default in the `outputs` folder of
your user folder). A config file holds only the options you change (`defaults` prints them all); nested options such
as `settings` or `skill_levels` are merged key by key. `ck-dps-solver search --help` lists the options. The save folder
is `%USERPROFILE%\AppData\LocalLow\Pugstorm\Core Keeper\Steam\<your Steam id>`.

## Development

```
src/ck_dps_solver/      the package
  model/                game rules and data: items, the character, talents, pets, food, progression, item sources
  engine/               the DPS formula and the search (solver.py runs a search)
  saves/                reading Core Keeper saves
  app/                  the Qt window
  defaults.py           the default options; catalogue.py, every searchable item
  data/                 the wiki data and icons
tests/                  python -m unittest discover tests
tools/                  the wiki data pipeline and checks
packaging/              the Windows app (PyInstaller)
docs/                   developer guides
```

- **Tests**: `python -m unittest discover tests` checks the app against values read in game (skill levels, max
  health, armor, damage ranges, dish effects, talent tree rules) and the search engine against single loadouts. Set
  `CK_FAST_TESTS=1` to skip the engine check. They run from the repository without installing (and on every push, in
  GitHub Actions).
- **Wiki data**: `python -m tools.wiki.build_data` rebuilds `src/ck_dps_solver/data/wiki_data.json`,
  `python -m tools.wiki.scan_updates` checks the wiki for game updates, `python -m tools.wiki.item_code` writes
  catalogue entries, and `python -m tools.verify` checks the catalogue and the engine. Please keep wiki requests few
  and slow.
- **Testing in game**: [docs/unknowns-and-assumptions.md](docs/unknowns-and-assumptions.md) lists what the solver
  assumes and how to check it in game; results make the app more accurate.
- **Adding a damage type**: see [docs/adding-a-damage-type.md](docs/adding-a-damage-type.md).
- **Windows app**: `pip install .[build]`, then `pyinstaller packaging/ck-dps-solver.spec` builds it in
  `dist/CK DPS Solver/`. `"CK DPS Solver.exe" --self-test` checks a build without opening the window: it runs a small
  search and the cooking planner, and writes `self_test.log` to the user folder (exit code 0 = passed).
- **Releasing**: update `__version__` in `src/ck_dps_solver/__init__.py` and add a section to
  [CHANGELOG.md](CHANGELOG.md), then push a tag: `git tag v1.0.0 && git push origin v1.0.0`. GitHub Actions builds
  the app, self-tests it, and publishes a release with the zip and the changelog section as its notes.

### Crash log
Errors are written to `crash.log` in the user folder (`%LOCALAPPDATA%\ck-dps-solver`), and the window says so.
Please include it when [reporting a problem](https://github.com/sinisterbot7900/ck-dps-solver/issues).

## Credits and license

- Code: [MIT License](LICENSE).
- Game data in `src/ck_dps_solver/data/wiki_data.json` comes from the [Core Keeper Fandom wiki](https://core-keeper.fandom.com) and is
  licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); changes to it must be shared under
  the same license.
- Icons in `src/ck_dps_solver/data/icons/` are Core Keeper game art from the wiki. Core Keeper and its art are © Pugstorm and
  Fireshine Games.
- This is a fan project, not affiliated with or endorsed by Pugstorm or Fireshine Games.
