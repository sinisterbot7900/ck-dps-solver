"""The DPS formula.

`dps_core` is written once, in plain Python on number arrays, so it runs both as ordinary Python (calculate_dps,
one loadout at a time) and compiled with numba (engine/batch_search.py, billions of loadouts). Keep it
numba-compatible: plain arithmetic, math functions, if/else; no dicts, strings or Python objects.

Magic weapons spend mana (wiki model): max mana 100 plus items, regeneration 10/s plus items, halved for 1 sec after
each attack. If you spend faster than you regenerate, you attack at full speed until mana runs out, then only as
fast as regeneration allows, for the rest of the 'Fight length' setting. Bonuses based on remaining mana (Fully
charged, Mage Mid set) are averaged over the attacks: mana falls linearly while it lasts, then stays near empty.

Poison you apply is a chance per hit; it lasts 15 sec and reapplying resets it. Bonuses against poisoned targets
(Potent poison, Druidra's Ring) and the Ivy set count for the share of the fight targets are poisoned: the wait for
the first poison, and gaps longer than 15 sec between poisons. An attacking pet's poison counts as keeping targets
poisoned (its attack rate isn't modeled), but not for the Ivy set, which needs poison you apply.
"""
import math

import numba
import numpy as np

from ck_dps_solver.model import Character
from ck_dps_solver.model.character import ACTIVE_EFFECTS_DICT, BURN_SOURCE, count_set_pieces
from ck_dps_solver.paths import can_cache

CACHE = can_cache(__file__) # numba's compiled cache needs the source (see paths.py)

# Attribute order of the `e` array
ATTRIBUTES = list(ACTIVE_EFFECTS_DICT.keys())
_A = {k: i for i, k in enumerate(ATTRIBUTES)}
DAMAGE, MELEE, RANGE, MINING_PCT = _A['%_damage'], _A['%_physical_melee_damage'], _A['%_physical_range_damage'], _A['%_mining_damage']
MELEE_ANY, RANGE_ANY = _A['%_melee_damage'], _A['%_range_damage']
MELEE_AS, RANGE_AS, BOTH_AS = _A['%_melee_attack_speed'], _A['%_range_attack_speed'], _A['%_melee_and_range_attack_speed']
BOSS, CRIT_DAMAGE, CRIT_CHANCE, TRIPLE = _A['%_damage_against_bosses'], _A['%_critical_hit_damage'], _A['%_critical_hit_chance'], _A['%_triple_hit_chance']
VS_BURNING, CRIT_DAMAGE_VS_BURNING = _A['%_damage_against_burning'], _A['%_critical_hit_damage_against_burning']
FISHING, MINING, THORNS = _A['+_fishing'], _A['+_mining_damage'], _A['+_thorns_damage']
RANGE_STANDING_STILL, MELEE_AS_PROC = _A['%_range_damage_while_standing_still'], _A['%_melee_attack_speed_proc_chance']
MAGIC, MAGIC_NEAR_WATER, MAGIC_FROM_MANA, MAGIC_ON_CRIT = _A['%_magic_damage'], _A['%_magic_damage_near_water'], _A['%_magic_damage_from_mana'], _A['%_magic_damage_on_crit']
MAX_MANA, MANA_REGEN, MANA_REGEN_CASTING, MANA_REGEN_DELAY = _A['+_max_mana'], _A['+_mana_regen'], _A['%_mana_regen_while_casting'], _A['%_mana_regen_delay_reduction']
BARRIER, BARRIER_AS_DAMAGE, BARRIER_AS_MANA = _A['+_magic_barrier'], _A['%_barrier_as_magic_damage'], _A['%_barrier_as_mana_regen']
POISON_CHANCE, PET_POISON = _A['%_chance_to_apply_poison'], _A['%_pet_poison_chance']
MINION_DAMAGE, MINION_AS, MINION_CRIT, MINION_CRIT_DAMAGE, MINION_BOSS = (_A['%_minion_damage'], _A['%_minion_attack_speed'], _A['%_minion_critical_hit_chance'],
                                                                      _A['%_minion_critical_hit_damage'], _A['%_minion_damage_against_bosses'])
MAX_MINIONS, RESERVATION_REDUCTION, MAGIC_TO_MINION = _A['+_max_minions'], _A['%_mana_reservation_reduction'], _A['%_magic_to_minion_damage']
MAX_HEALTH, MAX_HEALTH_PCT = _A['+_max_health'], _A['%_max_health']
EXPLOSIVES, NAPALM_CHANCE, BURNING_DAMAGE = _A['%_explosives_damage'], _A['%_napalm_chance'], _A['%_burning_damage']
VS_POISONED, CRIT_CHANCE_AFTER_POISONING = _A['%_damage_against_poisoned'], _A['%_critical_hit_chance_after_poisoning']

# Sets and groups the formula itself uses (order of the `counts` array)
FORMULA_SETS = ['ScarabSet', 'DiverSet', 'MinerSet', 'AncientGemRingAndNecklace', BURN_SOURCE, 'SkullRingAndNecklace', 'PlateSet', 'CoreCommanderSet']
SCARAB, DIVER, MINER, ANCIENT_GEM, BURN, SKULL, PLATE, CORE_COMMANDER = range(len(FORMULA_SETS))
# Pieces of each formula set the formula needs before the set does anything (see weapon_dps)
FORMULA_SET_PIECES = {'ScarabSet': 3, 'DiverSet': 3, 'MinerSet': 5, 'AncientGemRingAndNecklace': 2, BURN_SOURCE: 1,
                      'SkullRingAndNecklace': 3, 'PlateSet': 2, 'CoreCommanderSet': 3}

# Weapon, talent and setting values (order of the `p` array)
PARAMS = ['min_damage', 'max_damage', 'attacks_per_second', 'is_range', 'well_trained_aim', 'miners_strength', 'weakness_detection',
          'fast_and_furious', 'standing_still', 'burning', 'vs_boss',
          'is_magic', 'mana_cost', 'mana_channeling', 'arcane_frenzy', 'mental_defense', 'fight_length', 'near_water', 'full_barrier', 'optimistic',
          'is_summon', 'heartbound_horde', 'aura_damage', 'scepter_min', 'scepter_max', 'scepter_aps', 'scepter_mana', 'group_effort', 'tough_gang',
          'power_in_numbers', 'cursed', 'is_explosive', 'explosive_damage', 'burst_mana']
(P_MIN, P_MAX, P_APS, P_IS_RANGE, P_AIM, P_MINER, P_WEAKNESS, P_FAST_AND_FURIOUS, P_STANDING_STILL, P_BURNING, P_VS_BOSS,
 P_IS_MAGIC, P_MANA_COST, P_CHANNELING, P_FRENZY, P_MENTAL_DEFENSE, P_FIGHT_LENGTH, P_NEAR_WATER, P_FULL_BARRIER, P_OPTIMISTIC,
 P_IS_SUMMON, P_HEARTBOUND, P_AURA, P_S_MIN, P_S_MAX, P_S_APS, P_S_MANA, P_GROUP_EFFORT, P_TOUGH_GANG, P_POWER_IN_NUMBERS, P_CURSED,
 P_IS_EXPLOSIVE, P_EXPLOSIVE, P_BURST_MANA) = range(len(PARAMS))

ARCANE_FRENZY_SECONDS = 6 # Checked by the user
POISON_SECONDS = 15 # Checked by the user; reapplying resets it
MINION_BASE_CRIT_DAMAGE = 0.5 # Assumed the same as yours
CURSE_MULTIPLIER = 1.4 # Cursed targets take 40% more damage from minions
# Napalm (wiki object data): a patch lasting 5 sec that hits for 12 every 0.5 sec and burns for 17 every 2 sec.
# Overlapping patches all count; burning only once (it doesn't stack). Burning damage bonuses (After Burn) scale both.
NAPALM_SECONDS, NAPALM_HIT_DPS, NAPALM_BURN_DPS = 5.0, 24.0, 8.5
ON_CRIT_MAGIC_SECONDS = 3 # Soaring set: assumed


def params(weapon, perks, settings, optimistic=False):
    """optimistic: for upper bounds. Bonuses based on remaining mana count as at full mana, and regeneration is halved
    as if attacking at the weapon's base speed, so the result is never below the real DPS and never decreases when any
    stat increases (including attack speed)."""
    magic = perks['Magic']
    return np.array([weapon.min_damage, weapon.max_damage, weapon.attacks_per_second, 1.0 if weapon.delivery=='Range' else 0.0,
                     perks['Fishing']['Well-trained aim'], perks['Mining']['Miner\'s strength'], perks['Range']['Weakness detection'],
                     perks['Melee']['Fast and furious'], settings['Standing still'], settings['Burning'], settings['Vs boss'],
                     1.0 if weapon.damage_type=='Magic' else 0.0, weapon.mana_cost, magic['Mana channeling'], magic['Arcane frenzy'],
                     magic['Mental defense'], settings['Fight length'], settings['Adjacent to water'], settings['Full barrier'],
                     1.0 if optimistic else 0.0,
                     1.0 if weapon.damage_type=='Summoning' else 0.0, perks['Summoning']['Heartbound horde'], weapon.aura_damage,
                     getattr(weapon, 'scepter_min_damage', 0), getattr(weapon, 'scepter_max_damage', 0), getattr(weapon, 'scepter_attacks_per_second', 0),
                     getattr(weapon, 'scepter_mana_cost', 0), perks['Summoning']['Group effort'], perks['Summoning']['Tough gang'],
                     perks['Summoning']['Power in numbers'], 1.0 if settings['Cursed target'] and getattr(weapon, 'curses', False) else 0.0,
                     1.0 if weapon.damage_type=='Explosives' else 0.0, weapon.explosive_damage,
                     1.0 if settings.get('Burst at full mana', True) else 0.0], dtype=np.float64)


def formula_set_counts(set_counts):
    return np.array([set_counts.get(s, 0) for s in FORMULA_SETS], dtype=np.int64)


def explosion_dps(e, p, explosions_per_second):
    """Explosions: only explosives bonuses (no crits, triple hits, generic or boss damage), plus napalm they spawn"""
    if p[P_EXPLOSIVE] <= 0 or explosions_per_second <= 0:
        return 0.0
    dps = p[P_EXPLOSIVE] * (1 + e[EXPLOSIVES]) * explosions_per_second
    napalm_per_second = e[NAPALM_CHANCE] * explosions_per_second
    if napalm_per_second > 0:
        dps = dps + (napalm_per_second * NAPALM_SECONDS * NAPALM_HIT_DPS + NAPALM_BURN_DPS) * (1 + e[BURNING_DAMAGE])
    return dps


explosion_dps = numba.njit(cache=CACHE)(explosion_dps)


def weapon_dps(e, counts, p):
    """DPS (floored) of the weapon you attack with (everything but minions)"""
    if p[P_IS_EXPLOSIVE] > 0: # Grenades: a fixed throw rate
        return math.floor(explosion_dps(e, p, p[P_APS]))
    damage = e[DAMAGE]
    crit_damage = e[CRIT_DAMAGE]
    is_range = p[P_IS_RANGE] > 0
    is_magic = p[P_IS_MAGIC] > 0
    # Targets burn from any burn-on-hit item, the Skull 3-piece burn aura, or the Welder 2-piece while you burn,
    # enabling the "against burning targets" bonuses
    burning_targets = counts[BURN] >= 1 or counts[SKULL] >= 3 or (p[P_BURNING] > 0 and counts[PLATE] >= 2)
    if burning_targets:
        damage = damage + e[VS_BURNING]
        crit_damage = crit_damage + e[CRIT_DAMAGE_VS_BURNING]

    # Critical hits and attack speed follow how the weapon hits (range or melee)
    if is_range:
        # Weakness detection: chance per hit for 100% crit chance for 3 sec (procs don't extend it)
        critical_hit_chance = e[CRIT_CHANCE]
        weakness_uptime = 0.0
        if p[P_WEAKNESS] != 0:
            attacks_per_second = p[P_APS] * (1 + e[RANGE_AS] + e[BOTH_AS])
            expected_seconds_until_outcome = (1 / (p[P_WEAKNESS] * 0.02)) / attacks_per_second
            active_likelihood = 3 / (3 + expected_seconds_until_outcome) # Activation length / expected length of the block of time in and out of activation
            critical_hit_chance = active_likelihood + (e[CRIT_CHANCE] * (1 - active_likelihood))
            weakness_uptime = active_likelihood
        damage_type_attack_speed = e[RANGE_AS]
    else:
        critical_hit_chance = e[CRIT_CHANCE]
        weakness_uptime = 0.0
        # Fast and furious and item procs (e.g. Rune Song) are the same condition, so their chances add.
        # Buff grants +50% melee attack speed for 2 sec; procs during the buff don't extend it
        damage_type_attack_speed = e[MELEE_AS]
        proc_chance = p[P_FAST_AND_FURIOUS] * 0.02 + e[MELEE_AS_PROC]
        if proc_chance > 0:
            attacks_per_second = p[P_APS] * (1 + e[MELEE_AS] + e[BOTH_AS])
            expected_seconds_until_outcome = (1 / max(proc_chance, 1e-9)) / attacks_per_second
            active_likelihood = 2 / (2 + expected_seconds_until_outcome)
            damage_type_attack_speed = ((e[MELEE_AS] + 0.5) * active_likelihood) + (e[MELEE_AS] * (1 - active_likelihood))
    critical_hit_chance = min(critical_hit_chance, 1.)
    attacks_per_second = p[P_APS] * (1 + damage_type_attack_speed + e[BOTH_AS])

    # Damage bonuses: general, then by delivery (range/melee damage of any kind), then by damage type
    delivery_damage = e[RANGE_ANY] if is_range else e[MELEE_ANY]
    # Range damage after standing still (e.g. Chime Necklace), like the Focused accuracy talent
    if is_range and p[P_STANDING_STILL] > 0:
        delivery_damage = delivery_damage + e[RANGE_STANDING_STILL]
    attack_fraction = 1.0 # Share of attacks mana allows
    barrier = 0.0
    mana_fraction = 1.0 # Average remaining mana (share of max) when attacking
    if is_magic:
        max_mana = e[MAX_MANA]
        if p[P_FULL_BARRIER] > 0:
            # Mental defense: 20% per point of the max mana above the base 100 is added as barrier
            barrier = e[BARRIER] + p[P_MENTAL_DEFENSE] * 0.2 * max(max_mana - 100, 0.0)
        # Mana channeling: 10% per point of the mana cost back on a critical hit
        spend = attacks_per_second * p[P_MANA_COST] * (1 - min(p[P_CHANNELING] * 0.1 * critical_hit_chance, 1.0))
        # Regeneration is halved for 1 sec after each attack (less with regen delay reduction)
        halved_share = min(attacks_per_second * max(1 - e[MANA_REGEN_DELAY], 0.0), 1.0)
        if p[P_OPTIMISTIC] > 0:
            # Bound: the weapon's own attack speed (no item or talent lowers attack speed), so regen is never underestimated
            halved_share = min(p[P_APS] * max(1 - e[MANA_REGEN_DELAY], 0.0), 1.0)
        regen = e[MANA_REGEN] * (1 - 0.5 * halved_share) * (1 + e[MANA_REGEN_CASTING]) + barrier * e[BARRIER_AS_MANA]
        if spend > regen:
            fight = p[P_FIGHT_LENGTH]
            burst_seconds = max_mana / (spend - regen) # Full speed until mana runs out
            # Waiting (no attacks): regeneration at the full rate, after the moment it stays halved after the last attack
            idle_regen = e[MANA_REGEN] + barrier * e[BARRIER_AS_MANA]
            if fight <= burst_seconds:
                mana_fraction = 1 - fight / (2 * burst_seconds)
            elif p[P_BURST_MANA] > 0 and idle_regen > 0:
                # "Burst at full mana": attack until mana runs out, wait for it to refill, burst again
                if p[P_OPTIMISTIC] > 0:
                    # Bound: never more mana than max mana plus full-rate regeneration over the whole fight
                    attack_fraction = min(1.0, (max_mana + idle_regen * fight) / (spend * fight))
                else:
                    # After the first burst (from full mana): wait to refill, burst to empty, again. Waiting only pays if a
                    # cycle attacks longer than casting whenever there's mana would; else play as "spend as it comes".
                    # The last cycle waits only as long as there's time left to spend what it gains.
                    delay = max(1 - e[MANA_REGEN_DELAY], 0.0) # Regeneration stays halved this long after the last attack
                    halved_regen = 0.5 * e[MANA_REGEN] + barrier * e[BARRIER_AS_MANA]
                    drain = spend - regen # Mana per second while bursting
                    if max_mana <= halved_regen * delay:
                        refill = max_mana / halved_regen
                    else:
                        refill = delay + (max_mana - halved_regen * delay) / idle_regen
                    cycle = refill + burst_seconds
                    if burst_seconds / cycle <= regen / spend:
                        burst_attacks = attacks_per_second * burst_seconds # Waiting doesn't pay: spend as it comes
                        sustained_attacks = attacks_per_second * (regen / spend) * (fight - burst_seconds)
                        attack_fraction = (burst_attacks + sustained_attacks) / (attacks_per_second * fight)
                        mana_fraction = burst_attacks * 0.5 / (burst_attacks + sustained_attacks)
                    else:
                        cycles = math.floor((fight - burst_seconds) / cycle)
                        left = fight - burst_seconds - cycles * cycle # The last, shorter cycle: wait w, then burst what it gained
                        wait = left / (1 + halved_regen / drain)
                        if wait > delay:
                            wait = (left - (halved_regen - idle_regen) * delay / drain) / (1 + idle_regen / drain)
                        gained = halved_regen * wait if wait <= delay else halved_regen * delay + idle_regen * (wait - delay)
                        last = left - wait
                        last_mana = gained / (2 * max_mana) # Average mana during the last burst (share of max)
                        if last < left * regen / spend: # Too little time left to wait: keep casting instead
                            last, last_mana = left * regen / spend, 0.0
                        attacking = (1 + cycles) * burst_seconds + last
                        attack_fraction = attacking / fight
                        # Bursts run from full mana to empty
                        mana_fraction = ((1 + cycles) * burst_seconds * 0.5 + last * last_mana) / attacking
            else:
                burst_attacks = attacks_per_second * burst_seconds
                sustained_attacks = attacks_per_second * (regen / spend) * (fight - burst_seconds)
                attack_fraction = (burst_attacks + sustained_attacks) / (attacks_per_second * fight)
                mana_fraction = burst_attacks * 0.5 / (burst_attacks + sustained_attacks)
            # Attacks per second overall: min(attack speed, (max mana + regen x fight) / (cost x fight)), which never
            # decreases with any stat; only the mana-based bonuses can (used in the optimistic bound)
            if p[P_OPTIMISTIC] > 0:
                mana_fraction = 1.0

    # Poison: share of the fight targets are poisoned by you. Poisons come at rate r = chance x attacks per second;
    # the first one takes a while (average uptime over the fight, starting unpoisoned: 1 - (1 - e^-rL) / rL), and
    # poison stays up as long as the next one comes within 15 sec (1 - e^-15r)
    attack_rate = attacks_per_second * attack_fraction
    poisons_per_second = e[POISON_CHANCE] * attack_rate
    own_poison_uptime = 0.0
    if poisons_per_second > 0:
        expected_poisons = poisons_per_second * p[P_FIGHT_LENGTH]
        onset = 1 - (1 - math.exp(-expected_poisons)) / expected_poisons if expected_poisons > 0 else 0.0
        own_poison_uptime = (1 - math.exp(-POISON_SECONDS * poisons_per_second)) * onset
    target_poison_uptime = 1.0 if e[PET_POISON] > 0 else own_poison_uptime
    if e[VS_POISONED] != 0 and target_poison_uptime > 0:
        damage = damage + e[VS_POISONED] * target_poison_uptime
    # Ivy set: extra crit chance while your poison is up (before Weakness detection's 100% and the cap)
    if e[CRIT_CHANCE_AFTER_POISONING] != 0 and own_poison_uptime > 0:
        poisoned_crit = min(weakness_uptime + ((e[CRIT_CHANCE] + e[CRIT_CHANCE_AFTER_POISONING]) * (1 - weakness_uptime)), 1.)
        critical_hit_chance = poisoned_crit * own_poison_uptime + critical_hit_chance * (1 - own_poison_uptime)

    if is_magic:
        # Buffs on critical hit (Arcane frenzy, Soaring set): share of time up, procs during a buff don't extend it
        crits_per_second = critical_hit_chance * attacks_per_second * attack_fraction
        frenzy_uptime, on_crit_uptime = 0.0, 0.0
        if crits_per_second > 0:
            frenzy_uptime = ARCANE_FRENZY_SECONDS / (ARCANE_FRENZY_SECONDS + 1 / crits_per_second)
            on_crit_uptime = ON_CRIT_MAGIC_SECONDS / (ON_CRIT_MAGIC_SECONDS + 1 / crits_per_second)
        type_damage = e[MAGIC] + p[P_FRENZY] * 0.1 * frenzy_uptime + e[MAGIC_ON_CRIT] * on_crit_uptime + e[MAGIC_FROM_MANA] * mana_fraction
        if p[P_NEAR_WATER] > 0:
            type_damage = type_damage + e[MAGIC_NEAR_WATER]
        flat = barrier * e[BARRIER_AS_DAMAGE] # The best offense, Mage Low set: share of barrier as magic damage per hit
    else:
        type_damage = e[RANGE] if is_range else e[MELEE]
        # Flat damage from fishing (range) or mining (melee)
        if is_range:
            flat = e[FISHING] * ((p[P_AIM] * 0.06) + (0.24 if counts[DIVER] >= 3 else 0.0))
        else:
            flat = e[MINING] * (1 + e[MINING_PCT]) * ((p[P_MINER] * 0.02) + (0.08 if counts[MINER] >= 5 else 0.0) + (0.13 if counts[ANCIENT_GEM] >= 2 else 0.0))

    # Weapon damage, plus flat damage from thorns (Scarab set) and the flat damage above
    multiplier = 1 + damage + type_damage + delivery_damage
    min_damage = p[P_MIN] * multiplier
    max_damage = p[P_MAX] * multiplier
    thorns = e[THORNS] if counts[SCARAB] >= 3 else 0.0
    thorns_min = thorns * 0.9 * multiplier
    thorns_max = thorns * 1.1 * multiplier
    flat_min = flat * 0.9 * multiplier
    flat_max = flat * 1.1 * multiplier
    average_damage = (math.ceil(min_damage + flat_min + thorns_min) + math.floor(max_damage + flat_max + thorns_max)) / 2

    crit_adjusted_damage = average_damage * (critical_hit_chance * (1 + crit_damage))
    crit_adjusted_damage = crit_adjusted_damage + average_damage * (1 - critical_hit_chance)
    triple_adjusted_damage = crit_adjusted_damage * e[TRIPLE] * 3
    triple_adjusted_damage = triple_adjusted_damage + crit_adjusted_damage * (1 - e[TRIPLE])

    boss_damage = e[BOSS] if p[P_VS_BOSS] > 0 else 0.0
    final_dps = triple_adjusted_damage * attacks_per_second * attack_fraction * (1 + boss_damage)
    # Core Commander 3-piece aura: 67 radioactive damage every other second (flat, unscaled)
    if counts[CORE_COMMANDER] >= 3:
        final_dps = final_dps + 67 / 2
    # Mortars and zookas: an explosion every shot, on top of the range hit
    final_dps = final_dps + explosion_dps(e, p, attacks_per_second * attack_fraction)
    return math.floor(final_dps)


weapon_dps = numba.njit(cache=CACHE)(weapon_dps)


def minion_dps(e, p, minions, magic_bonus):
    """Summoning: DPS of `minions` minions. Minions only get effects that say minion, plus Trickle down arcana and the
    Grim set's share of your magic damage bonus (magic_bonus). p's damage and attack speed are the minion's."""
    if minions < 1:
        return 0.0
    # Heartbound horde: minion attack speed for every 10 max health
    max_health = math.floor(e[MAX_HEALTH] * (1 + e[MAX_HEALTH_PCT]) + 0.5) # Rounded to the nearest, as the game shows it
    attack_speed = e[MINION_AS] + p[P_HEARTBOUND] * 0.001 * math.floor(max_health / 10)
    multiplier = 1 + e[MINION_DAMAGE] + e[MAGIC_TO_MINION] * magic_bonus
    average_damage = (math.ceil(p[P_MIN] * multiplier) + math.floor(p[P_MAX] * multiplier)) / 2
    critical_hit_chance = min(e[MINION_CRIT], 1.)
    per_hit = average_damage * (1 + critical_hit_chance * (MINION_BASE_CRIT_DAMAGE + e[MINION_CRIT_DAMAGE]))
    target = 1 + e[MINION_BOSS] if p[P_VS_BOSS] > 0 else 1.0
    if p[P_CURSED] > 0:
        target = target * CURSE_MULTIPLIER
    # Auras (e.g. the Radioactive Minion's radiation) don't stack between minions: counted once
    return minions * per_hit * p[P_APS] * (1 + attack_speed) * target + p[P_AURA] * multiplier * target


minion_dps = numba.njit(cache=CACHE)(minion_dps)


def summoner_dps(e, counts, p):
    """Summoning: minions plus the scepter you attack with (if any). Minions reserve mana, leaving less for the scepter, so
    this takes the best number of minions to summon, up to the most that fit with room for one scepter cast."""
    has_scepter = p[P_S_APS] > 0
    reservation = p[P_MANA_COST] * max(1 - e[RESERVATION_REDUCTION], 0.0)
    most = 1 + e[MAX_MINIONS]
    if p[P_OPTIMISTIC] == 0 and reservation > 0:
        room = e[MAX_MANA] - (p[P_S_MANA] if has_scepter else 0.0)
        most = min(most, math.floor(room / reservation))
    most = max(most, 0.0)
    if not has_scepter:
        return math.floor(minion_dps(e, p, most, e[MAGIC] + p[P_GROUP_EFFORT] * 0.02 * most))
    e2 = e.copy()
    p2 = p.copy()
    p2[P_IS_SUMMON] = 0.0
    p2[P_IS_MAGIC] = 1.0
    p2[P_IS_RANGE] = 1.0
    p2[P_MIN] = p[P_S_MIN]
    p2[P_MAX] = p[P_S_MAX]
    p2[P_APS] = p[P_S_APS]
    p2[P_MANA_COST] = p[P_S_MANA]
    p2[P_AURA] = 0.0
    best = 0.0
    fewest = most if p[P_OPTIMISTIC] > 0 else 0.0 # The bound: all minions, and the scepter keeps all your mana
    minions = most
    while minions >= fewest:
        # Group effort: magic damage per minion; Tough gang: barrier per minion; Power in numbers: range attack speed per minion
        magic_bonus = e[MAGIC] + p[P_GROUP_EFFORT] * 0.02 * minions
        e2[MAGIC] = magic_bonus
        e2[BARRIER] = e[BARRIER] + p[P_TOUGH_GANG] * 15 * minions
        e2[RANGE_AS] = e[RANGE_AS] + p[P_POWER_IN_NUMBERS] * 0.01 * minions
        e2[MAX_MANA] = e[MAX_MANA] - (minions * reservation if p[P_OPTIMISTIC] == 0 else 0.0)
        total = minion_dps(e, p, minions, magic_bonus) + weapon_dps(e2, counts, p2)
        if total > best:
            best = total
        minions -= 1
    return math.floor(best)


summoner_dps = numba.njit(cache=CACHE)(summoner_dps)


def dps_core(e, counts, p):
    """DPS (floored) from summed attributes `e`, formula set piece `counts` and weapon/talent/setting values `p`"""
    if p[P_IS_SUMMON] > 0:
        return summoner_dps(e, counts, p)
    return weapon_dps(e, counts, p)


dps_core_compiled = numba.njit(cache=CACHE)(dps_core)


def attribute_array(active_effects):
    return np.array([active_effects[k] for k in ATTRIBUTES], dtype=np.float64)


def dps_from_effects(weapon, perks, settings, active_effects, set_counts, optimistic=False):
    """DPS from summed active effects {attribute: value} and set piece counts {set: pieces} (plain Python)"""
    return dps_core(attribute_array(active_effects), formula_set_counts(set_counts), params(weapon, perks, settings, optimistic))


def calculate_dps(character: Character):
    active_effects_sources, set_keywords = character.get_active_effects()
    active_effects = {k: sum(v.values()) for k, v in active_effects_sources.items()}
    return int(dps_from_effects(character.items['Weapon'], character.perks, character.settings, active_effects, count_set_pieces(set_keywords)))
