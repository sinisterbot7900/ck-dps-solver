# Unknowns and assumptions you can test

The solver's numbers come from the [Core Keeper wiki](https://core-keeper.fandom.com)'s data. The wiki doesn't cover
everything: buff durations, stacking rules, minion behavior and a few hidden bonuses aren't in it. Where a value
couldn't be found, the solver makes an assumption, listed below. If you can test one in game, your result will make the
app more accurate.

To report a result, open a [Game test result issue](https://github.com/sinisterbot7900/ck-dps-solver/issues/new?template=game_test_result.md)
with what you did and what you saw. Screenshots of the character screen or item tooltips help. Values that have
already been checked in game are listed at the end, so you don't need to retest them.

**Tips for testing**
- Test on a training dummy or a weak enemy that won't die, and turn off other damage sources (pets, minions, thorns).
- Damage numbers vary ±10% per hit. Note several hits, or the lowest and highest you see.
- The character screen (C) shows your stats with everything equipped; compare it with the solver's Stats panel
  (click a loadout on the Search tab).

## Summoning

- **Minion critical hit damage.** Assumed: minions crit for +50% damage, like you do.
  Test: summon a minion, watch its hits, and compare a crit's number with a normal hit's.
- **Minion attack speed.** Each tome's minion attacks on a fixed cycle taken from the wiki's tome pages (for example
  1.66 seconds for the bat, 1.83 for the melee minion). Orbiting and radiating minions are assumed to stay in contact
  with the target and hit every 0.5 seconds.
  Test: count a minion's hits on a dummy over 10–20 seconds.
- **Tome of Breach.** Not searched: its pickaxe minion's attack rate isn't known.
  Test: count its hits over time, as above.
- **Power in numbers for other damage types.** Range and magic users are assumed to keep one minion out ("Summon active"
  setting), for 1% range attack speed per point.
  Test: does the bonus apply with a minion out while you attack with a bow or staff, and does it scale with minions?
- **Desert Guardian set (3 pieces).** Minions exploding when they despawn isn't counted.

## Magic

- **Soaring set.** Its buff on critical hits is assumed to last 3 seconds.
  Test: time the buff icon after a crit.
- **Full barrier.** The best offense, the Mage Low set, Arcane transfusion and the Warped set assume your magic barrier
  stays full ("Full barrier" setting). The default magic talents rely on this.
  Test: how quickly does the barrier refill in a real fight, and does a partly full barrier still count?
- **Mana.** Uses the wiki's model: 100 max mana, 10 mana per second, halved for 1 second after each attack.
  Test: time how long a staff can attack nonstop before running out of mana.
- **Waiting for mana.** "Burst at full mana" assumes regeneration returns to the full rate 1 second after your last
  attack, and that Mana recharge (regeneration while casting) doesn't apply while you wait.
  Test: run out of mana, stop attacking, and time the refill to full; then compare with refilling while attacking.

## Combat settings and buffs

- **Stacking talents.** With "Range stacks", "Melee stacks" or "Running stacks" on, the stacking talents count for the
  whole fight at a fixed size: Keeping momentum and Building anger at 4% per talent point, Keeping tempo at 3% and
  Stubborn fighter at 3%. The real maximum stacks and their build-up time aren't confirmed.
  Test: with points in one of these talents, how high does the bonus go on the character screen, and how fast does it
  build up and fall off?
- **Weakness detection.** Modeled like Fast and furious (checked in game): while the buff is up, more procs don't
  extend it.
  Test: does Weakness detection's buff refresh when it procs again?
- **Poison.** Lasts 15 seconds (checked), and reapplying resets the timer (from the community, not tested here). An
  attacking pet's poison counts as always up.
  Test: does reapplying poison reset its timer? How often does a pet's poison actually land?
- **Low health.** The Octarine set and Desperate fighter assume the lowest "low health" (75% of health missing).
- **Fight length.** 60 seconds of nonstop attacking, starting at full mana with an unpoisoned target.

## Explosives

- **Napalm.** Overlapping napalm patches all deal damage; burning only counts once.
- **Sun Caller.** Its bouncing explosion isn't counted (it rarely hits).
- **Sulfur set (3 pieces).** The explosion when you take damage isn't counted.

## Effects that aren't modeled

Some items have effects the solver ignores, so items with them may be better than their DPS here. The damage-dealing
ones could be added if someone measures them:
- Chain lightning (lightning gun), thunder beams on crits, boss projectiles on hit (scarab, octopus), ghosts summoned
  on kills, fire spawned on attack, explosions on cursed enemies.

Not counted because they don't add damage directly: knockback, stun, slow, charm, slippery ground, and damage you take.
Each item lists its unmodeled effects in `src/ck_dps_solver/catalogue.py` ("Not modeled: ...").

## Character stats

- **Experience curves.** Game update 1.3.0.1 changed the experience needed per skill level, and the wiki still has the
  old curves. The new ones are fitted to levels read from five characters, so skill levels read from saves can be
  off by one near some level boundaries.
  Test: load your save and compare each skill's level on the Character tab with the game's skills screen. Report any
  skill where they differ, with both levels.
- **Hidden set bonuses.** The full Witch Doctor set gives +1 armor that its tooltip doesn't mention (found by testing).
  Other sets may have hidden bonuses too.
  Test: compare your armor and other stats on the character screen with the solver's Stats panel, with and without a
  full set.
- **Rounded wiki values.** Some wiki damage values are truncated, so a weapon can show 1 less than in game (the Simple
  Staff: 71 instead of 72).
  Test: compare a weapon's tooltip damage range with the solver's.
- **Reinforcement.** Owned gear is assumed reinforced (+15% stats) unless you choose "detected" on the Items tab.

## Food and cooking

- **Dish rarity.** A dish with a golden ingredient comes out rare (+25%); with both ingredients golden, +15% more.
  Epic dishes (+50%) only happen by chance with the Master chef talent, so they're never planned.
  Test: cook a pair of golden ingredients and compare the dish's effect with each ingredient's.
- **Stacking.** The same effect from two foods or potions only counts once, the stronger one. This follows the game
  data's stacking flag and was checked for one pair.
  Test: eat two foods with the same effect and see whether the character screen adds them up.

## Progression and item sources

- **Gate bosses.** Nimruza and Urschleim are treated as bosses you must beat to move on, which delays their drops by a
  tier. If they're optional, their drops should count in their own tier.
- **Boss refights.** Random boss drops count from the Forgotten Ruins at the earliest, because the Cloaked Merchant
  (after Ghorm) sells the summoning idols needed to fight a boss again.
- **Stolen Crystal Heart.** The wiki credits it to Malugaz; it's used to detect that you've beaten him.
- **Drop chances** come from the wiki and are shown as a range when crate or chest variants differ.

## Reading saves

- **Chests.** Storage chests (including the Iron Chest) count fully. Loot chests (dungeons, ruins) only count items
  you've picked up before, so unlooted dungeon loot isn't treated as yours.
  Test: if an item shows as owned but you don't have it, or the other way round, report which chest it's in.
- **Chest range.** Only chests within 300 tiles of your character count (Items tab, advanced settings).
- **Save timing.** The game only writes its save now and then, so recent changes may not show until you quit to the
  menu. How often it saves isn't known.

## Default talents

The default talents (`src/ck_dps_solver/defaults.py`) are the best legal build for each damage type at level 100. They
were found by trying every legal build of each skill on the best loadouts, one skill at a time, with the default
settings. Two skills changed together could in principle do better.

## Already checked in game

These have been tested, so they don't need retesting:
- Fast and furious: +50% melee attack speed for 2 seconds; procs during the buff don't extend it.
- Two copies of the same ring both count (a set counts the duplicate once).
- Low health means 25% health or less.
- Golem set (2 pieces): +20% damage against bosses, added to other boss damage.
- Poison lasts 15 seconds. Arcane frenzy lasts 6 seconds.
- A rare dish of Tornis Kingfish and Golden Bloat Oat gives 63% damage (50.4% × 1.25).
- Minions only get effects that say "minion".
- Max health: (100 + Vitality level + Maxed out! + permanent foods + gear) × (1 + Druidra soul + well fed), rounded to
  the nearest whole number.
- Reinforced armor rounds up.
- The Scarab set's thorns damage applies to magic weapons (each beam tick).
- Pet talent Triple Trouble: 2% triple hit chance per point.
- Weapon damage ranges for the Tin Hoe, Runestone Scepter, Sticky Stick and Wood Crossbow match the game.
