"""Every item the solver searches when you don't load a save: weapons, armor, jewelry, offhands, bags, lanterns and pets,
at level 20 (rebuilt at their base level for progression searches).

Generated from the wiki data by tools/wiki/item_code.py (--insert to add items, --sync to update them); edit consider_for
by hand to choose which damage types an item is tried for.
"""
from ck_dps_solver.model import Item, Weapon

WEAPONS = {
    'Galaxite Chakram': Weapon(
        name='Galaxite Chakram',
        min_damage=151,
        max_damage=185,
        attacks_per_second=2.5,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_critical_hit_damage': 0.52,
        },
    ),
    # Not modeled: MovementSpeedBoostAfterMining, LightningGunChainLightning
    'Stormbringer': Weapon(
        name='Stormbringer',
        min_damage=87,
        max_damage=107,
        attacks_per_second=5.0,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 1097.0,
        },
        has_durability=False,
    ),
    # Not modeled: ChanceOnHitToKnockback
    'Pipe Club': Weapon(
        name='Pipe Club',
        min_damage=626,
        max_damage=765,
        attacks_per_second=1.25,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Quill Rifle': Weapon(
        name='Quill Rifle',
        min_damage=85,
        max_damage=103,
        attacks_per_second=4.0,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.472,
        },
    ),
    # Not modeled: ChanceOnHitToKnockback
    'Anchor Axe': Weapon(
        name='Anchor Axe',
        min_damage=435,
        max_damage=531,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_damage': 0.43,
        },
    ),
    'Prehistoric Crystal Spear': Weapon(
        name='Prehistoric Crystal Spear',
        min_damage=320,
        max_damage=392,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.47,
        },
    ),
    'Atlantean Worm Sword': Weapon(
        name='Atlantean Worm Sword',
        min_damage=315,
        max_damage=385,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_damage_against_bosses': 0.21,
        },
    ),
    'Battle Axe': Weapon(
        name='Battle Axe',
        min_damage=450,
        max_damage=550,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.445,
        },
    ),
    'Blowpipe': Weapon(
        name='Blowpipe',
        min_damage=225,
        max_damage=275,
        attacks_per_second=1.6667,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_chance_to_apply_poison': 0.27,
        },
    ),
    'Broken Handle': Weapon(
        name='Broken Handle',
        min_damage=221,
        max_damage=271,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '+_max_health': 62.0,
        },
    ),
    # Not modeled: ChanceOnHitToApplySlipperyMovement
    'Bubble Gun': Weapon(
        name='Bubble Gun',
        min_damage=149,
        max_damage=183,
        attacks_per_second=2.5,
        damage_type='Range',
        consider_for='Range',
    ),
    'Burnzooka': Weapon(
        name='Burnzooka',
        min_damage=222,
        max_damage=272,
        attacks_per_second=0.6667,
        damage_type='Range',
        explosive_damage=488,
        consider_for='Range',
    ),
    'Splintered Wooden Sword': Weapon(
        name='Splintered Wooden Sword',
        min_damage=321,
        max_damage=393,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.19,
        },
    ),
    'Copper Sword': Weapon(
        name='Copper Sword',
        min_damage=314,
        max_damage=384,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
    ),
    # Not modeled: ChanceToApplyCharmed
    'Cupid Bow': Weapon(
        name='Cupid Bow',
        min_damage=38,
        max_damage=46,
        attacks_per_second=0.2,
        damage_type='Range',
        consider_for='Range',
    ),
    'Flintlock Musket': Weapon(
        name='Flintlock Musket',
        min_damage=724,
        max_damage=886,
        attacks_per_second=0.5,
        damage_type='Range',
        consider_for='Range',
    ),
    'Galaxite Dagger': Weapon(
        name='Galaxite Dagger',
        min_damage=264,
        max_damage=322,
        attacks_per_second=3.3333,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.18,
        },
    ),
    'Galaxite Sword': Weapon(
        name='Galaxite Sword',
        min_damage=312,
        max_damage=382,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_damage': 0.47,
        },
    ),
    'Grubzooka': Weapon(
        name='Grubzooka',
        min_damage=217,
        max_damage=265,
        attacks_per_second=0.6667,
        damage_type='Range',
        consider_for='Range',
    ),
    'Scrapzooka': Weapon(
        name='Scrapzooka',
        min_damage=57,
        max_damage=69,
        attacks_per_second=0.6667,
        damage_type='Range',
        explosive_damage=488,
        consider_for='Range',
    ),
    'Hunting Spear': Weapon(
        name='Hunting Spear',
        min_damage=320,
        max_damage=391,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.09,
        },
    ),
    # Not modeled: DamageIncreaseAgainstStunned
    'Hydra Bone Sword': Weapon(
        name='Hydra Bone Sword',
        min_damage=307,
        max_damage=375,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_damage_against_bosses': 0.18,
        },
    ),
    'Iron Bow': Weapon(
        name='Iron Bow',
        min_damage=262,
        max_damage=320,
        attacks_per_second=1.4286,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.453,
        },
    ),
    'Iron Halberd': Weapon(
        name='Iron Halberd',
        min_damage=309,
        max_damage=377,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Iron Sword': Weapon(
        name='Iron Sword',
        min_damage=312,
        max_damage=382,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.099,
        },
    ),
    # Not modeled: ChanceOnHitToKnockback
    'Larva Spike Club': Weapon(
        name='Larva Spike Club',
        min_damage=308,
        max_damage=376,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Lava Battle Axe': Weapon(
        name='Lava Battle Axe',
        min_damage=439,
        max_damage=537,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '+_burn_damage_on_hit': 66.0,
        },
    ),
    'Volcano Mortar': Weapon(
        name='Volcano Mortar',
        min_damage=26,
        max_damage=32,
        attacks_per_second=1.6667,
        damage_type='Range',
        explosive_damage=171,
        consider_for='Range',
        attributes={
            '+_burn_damage_on_hit': 68.0,
        },
    ),
    # Not modeled: ChanceOnKillToSummonGhost
    'Phantom Spark': Weapon(
        name='Phantom Spark',
        min_damage=260,
        max_damage=318,
        attacks_per_second=1.4286,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_critical_hit_damage': 0.34,
            '%_critical_hit_chance': 0.12,
        },
        has_durability=False,
    ),
    # Not modeled: IncreaseSequenceExplosionTotalMaxExplosionsOnHit
    'Credence of Ruin': Weapon(
        name='Credence of Ruin',
        min_damage=27,
        max_damage=33,
        attacks_per_second=1.6667,
        damage_type='Range',
        explosive_damage=171,
        consider_for='Range',
        has_durability=False,
    ),
    'Rune Song': Weapon(
        name='Rune Song',
        min_damage=349,
        max_damage=427,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed_proc_chance': 0.08,
        },
        has_durability=False,
    ),
    'Scrap Minigun': Weapon(
        name='Scrap Minigun',
        min_damage=51,
        max_damage=63,
        attacks_per_second=8.0,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.228,
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Octarine Axe': Weapon(
        name='Octarine Axe',
        min_damage=453,
        max_damage=553,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.18,
        },
    ),
    'Octarine Bow': Weapon(
        name='Octarine Bow',
        min_damage=252,
        max_damage=308,
        attacks_per_second=1.4286,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.091,
        },
    ),
    'Octarine Sword': Weapon(
        name='Octarine Sword',
        min_damage=311,
        max_damage=381,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.098,
        },
    ),
    # Not modeled: ChanceToAddRandomConditionOnHit
    'Pandorium Axe': Weapon(
        name='Pandorium Axe',
        min_damage=434,
        max_damage=530,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Poisonous Sickle': Weapon(
        name='Poisonous Sickle',
        min_damage=320,
        max_damage=392,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_damage': 0.26,
            '%_chance_to_apply_poison': 0.41,
        },
    ),
    'Ricochet Shuriken': Weapon(
        name='Ricochet Shuriken',
        min_damage=104,
        max_damage=128,
        attacks_per_second=2.5,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.053,
            '%_critical_hit_damage': 0.26,
        },
    ),
    'Ritual Dagger': Weapon(
        name='Ritual Dagger',
        min_damage=258,
        max_damage=316,
        attacks_per_second=3.3333,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_damage': 0.25,
            '%_critical_hit_chance': 0.09,
        },
    ),
    'Rusty Dagger': Weapon(
        name='Rusty Dagger',
        min_damage=256,
        max_damage=314,
        attacks_per_second=3.3333,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.16,
        },
    ),
    'Shellzooka': Weapon(
        name='Shellzooka',
        min_damage=57,
        max_damage=69,
        attacks_per_second=0.6667,
        damage_type='Range',
        explosive_damage=488,
        consider_for='Range',
    ),
    'Scarlet Crossbow': Weapon(
        name='Scarlet Crossbow',
        min_damage=296,
        max_damage=362,
        attacks_per_second=1.0,
        damage_type='Range',
        consider_for='Range',
    ),
    'Scarlet Dagger': Weapon(
        name='Scarlet Dagger',
        min_damage=252,
        max_damage=308,
        attacks_per_second=3.3333,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_damage': 0.44,
        },
    ),
    'Scarlet Sword': Weapon(
        name='Scarlet Sword',
        min_damage=307,
        max_damage=375,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.16,
        },
    ),
    # Not modeled: ChanceOnHitToKnockback
    'Crystal Shard Club': Weapon(
        name='Crystal Shard Club',
        min_damage=388,
        max_damage=474,
        attacks_per_second=2.0,
        damage_type='Melee',
        consider_for='Melee',
    ),
    # Not modeled: ApplyMovementSpeedReduction
    'Slime Sword': Weapon(
        name='Slime Sword',
        min_damage=268,
        max_damage=328,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Slingshot': Weapon(
        name='Slingshot',
        min_damage=184,
        max_damage=226,
        attacks_per_second=2.0,
        damage_type='Range',
        consider_for='Range',
    ),
    # Not modeled: ChanceOnHitToApplySlipperyMovement
    'Slippery Slime Sword': Weapon(
        name='Slippery Slime Sword',
        min_damage=310,
        max_damage=380,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Sniper Rifle': Weapon(
        name='Sniper Rifle',
        min_damage=560,
        max_damage=684,
        attacks_per_second=0.5,
        damage_type='Range',
        consider_for='Range',
    ),
    # Not modeled: ChanceOnRangeShotToStun
    'Snowball': Weapon(
        name='Snowball',
        min_damage=184,
        max_damage=226,
        attacks_per_second=2.0,
        damage_type='Range',
        consider_for='Range',
        has_durability=False,
    ),
    'Solarite Crossbow': Weapon(
        name='Solarite Crossbow',
        min_damage=257,
        max_damage=315,
        attacks_per_second=1.4286,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.221,
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Solarite Sword': Weapon(
        name='Solarite Sword',
        min_damage=311,
        max_damage=381,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.053,
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Stone Mortar': Weapon(
        name='Stone Mortar',
        min_damage=26,
        max_damage=32,
        attacks_per_second=1.6667,
        damage_type='Range',
        explosive_damage=171,
        consider_for='Range',
    ),
    'Tentacle Whip': Weapon(
        name='Tentacle Whip',
        min_damage=462,
        max_damage=564,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Throwing Daggers': Weapon(
        name='Throwing Daggers',
        min_damage=151,
        max_damage=185,
        attacks_per_second=2.5,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '%_critical_hit_chance': 0.19,
        },
    ),
    'Tin Axe': Weapon(
        name='Tin Axe',
        min_damage=440,
        max_damage=538,
        attacks_per_second=1.6667,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Tin Dagger': Weapon(
        name='Tin Dagger',
        min_damage=257,
        max_damage=315,
        attacks_per_second=3.3333,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Tin Sword': Weapon(
        name='Tin Sword',
        min_damage=308,
        max_damage=376,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Void Club': Weapon(
        name='Void Club',
        min_damage=368,
        max_damage=450,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Void Gun': Weapon(
        name='Void Gun',
        min_damage=297,
        max_damage=363,
        attacks_per_second=1.0,
        damage_type='Range',
        consider_for='Range',
    ),
    'Wood Bow': Weapon(
        name='Wood Bow',
        min_damage=207,
        max_damage=253,
        attacks_per_second=1.4286,
        damage_type='Range',
        consider_for='Range',
    ),
    'Wood Crossbow': Weapon(
        name='Wood Crossbow',
        min_damage=296,
        max_damage=362,
        attacks_per_second=1.0,
        damage_type='Range',
        consider_for='Range',
    ),
    'Wooden Sword': Weapon(
        name='Wooden Sword',
        min_damage=308,
        max_damage=376,
        attacks_per_second=2.5,
        damage_type='Melee',
        consider_for='Melee',
    ),
    'Obliteration Ray': Weapon(
        name='Obliteration Ray',
        min_damage=80,
        max_damage=98,
        attacks_per_second=5.0,
        damage_type='Melee',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 1073.0,
        },
    ),
    # Not modeled: ChanceToSpawnFireOnAttack
    'Flamethrower': Weapon(
        name='Flamethrower',
        min_damage=68,
        max_damage=84,
        attacks_per_second=5.0,
        damage_type='Range',
        consider_for='Range',
        attributes={
            '+_burn_damage_on_hit': 64.0,
        },
    ),
    'Corrosion Staff': Weapon(
        name='Corrosion Staff',
        min_damage=94,
        max_damage=116,
        attacks_per_second=5.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=8,
        consider_for='Magic',
        attributes={
            '+_mining_damage': 181.0,
        },
    ),
    'Arcane Staff': Weapon(
        name='Arcane Staff',
        min_damage=141,
        max_damage=173,
        attacks_per_second=3.3333,
        damage_type='Magic',
        delivery='Range',
        mana_cost=9,
        consider_for='Magic',
        attributes={
            '%_critical_hit_chance': 0.16,
        },
    ),
    'Withered Scepter': Weapon(
        name='Withered Scepter',
        min_damage=190,
        max_damage=232,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=26,
        curses=True,
        consider_for='Magic',
    ),
    'Simple Staff': Weapon(
        name='Simple Staff',
        min_damage=431,
        max_damage=527,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=30,
        consider_for='Magic',
        attributes={
            '%_critical_hit_chance': 0.17,
        },
    ),
    'Chaos Staff': Weapon(
        name='Chaos Staff',
        min_damage=470,
        max_damage=574,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=30,
        consider_for='Magic',
    ),
    'Hollowcore Scepter': Weapon(
        name='Hollowcore Scepter',
        min_damage=122,
        max_damage=148,
        attacks_per_second=1.4286,
        damage_type='Magic',
        delivery='Range',
        mana_cost=18,
        curses=True,
        consider_for='Magic',
    ),
    'Fireball Staff': Weapon(
        name='Fireball Staff',
        min_damage=436,
        max_damage=532,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=30,
        consider_for='Magic',
        attributes={
            '+_burn_damage_on_hit': 73.0,
        },
    ),
    # Not modeled: IncreaseCountCurseLegendaryExplosionOnHit
    'Veil Crux': Weapon(
        name='Veil Crux',
        min_damage=148,
        max_damage=180,
        attacks_per_second=1.4286,
        damage_type='Magic',
        delivery='Range',
        mana_cost=21,
        curses=True,
        consider_for='Magic',
        has_durability=False,
    ),
    # Not modeled: IncreaseManaCostAndMagicDamagePercentagePerSecond
    'Titan Breath': Weapon(
        name='Titan Breath',
        min_damage=48,
        max_damage=58,
        attacks_per_second=5.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=6,
        consider_for='Magic',
        attributes={
            '%_critical_hit_chance': 0.12,
            '+_mining_damage': 510.0,
        },
        has_durability=False,
    ),
    'Corrupted Meteor Staff': Weapon(
        name='Corrupted Meteor Staff',
        min_damage=944,
        max_damage=1154,
        attacks_per_second=0.5,
        damage_type='Magic',
        delivery='Range',
        mana_cost=60,
        consider_for='Magic',
        attributes={
            '%_critical_hit_damage': 0.45,
        },
    ),
    'Noxious Meteor Staff': Weapon(
        name='Noxious Meteor Staff',
        min_damage=958,
        max_damage=1170,
        attacks_per_second=0.5,
        damage_type='Magic',
        delivery='Range',
        mana_cost=60,
        consider_for='Magic',
        attributes={
            '%_chance_to_apply_poison': 0.25,
        },
    ),
    'Blightbloom Scepter': Weapon(
        name='Blightbloom Scepter',
        min_damage=125,
        max_damage=153,
        attacks_per_second=1.5385,
        damage_type='Magic',
        delivery='Range',
        mana_cost=17,
        curses=True,
        consider_for='Magic',
    ),
    # Not modeled: ChanceOnHitToStun
    'Pandoric Scepter': Weapon(
        name='Pandoric Scepter',
        min_damage=137,
        max_damage=167,
        attacks_per_second=1.4286,
        damage_type='Magic',
        delivery='Range',
        mana_cost=18,
        curses=True,
        consider_for='Magic',
    ),
    'Scholar\'s Staff': Weapon(
        name='Scholar\'s Staff',
        min_damage=430,
        max_damage=526,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=30,
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.382,
        },
    ),
    # Not modeled: ApplyExplodeCursedEnemy
    'Abyssal Scepter': Weapon(
        name='Abyssal Scepter',
        min_damage=127,
        max_damage=155,
        attacks_per_second=1.4286,
        damage_type='Magic',
        delivery='Range',
        mana_cost=18,
        curses=True,
        consider_for='Magic',
    ),
    # Not modeled: ApplySlowedBySlime
    'Sticky Stick': Weapon(
        name='Sticky Stick',
        min_damage=391,
        max_damage=477,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=30,
        consider_for='Magic',
    ),
    'Runestone Scepter': Weapon(
        name='Runestone Scepter',
        min_damage=108,
        max_damage=132,
        attacks_per_second=1.3333,
        damage_type='Magic',
        delivery='Range',
        mana_cost=19,
        curses=True,
        consider_for='Magic',
    ),
    'Sun Caller': Weapon(
        name='Sun Caller',
        min_damage=441,
        max_damage=539,
        attacks_per_second=1.0,
        damage_type='Magic',
        delivery='Range',
        mana_cost=36,
        consider_for='Magic',
        attributes={
            '%_critical_hit_chance': 0.18,
        },
    ),
    'Zealot\'s Scimitar': Weapon(
        name='Zealot\'s Scimitar',
        min_damage=433,
        max_damage=529,
        attacks_per_second=1.6667,
        damage_type='Magic',
        delivery='Melee',
        mana_cost=22,
        consider_for='Magic',
    ),
    'Tome of Ashes': Weapon(
        name='Tome of Ashes',
        min_damage=86,
        max_damage=106,
        attacks_per_second=0.578,
        damage_type='Summoning',
        delivery='Minion',
        mana_cost=15,
        consider_for='Summoning',
    ),
    'Tome of the Dead': Weapon(
        name='Tome of the Dead',
        min_damage=102,
        max_damage=124,
        attacks_per_second=0.5464,
        damage_type='Summoning',
        delivery='Minion',
        mana_cost=15,
        consider_for='Summoning',
    ),
    'Tome of the Deep': Weapon(
        name='Tome of the Deep',
        min_damage=78,
        max_damage=96,
        attacks_per_second=2.0,
        damage_type='Summoning',
        delivery='Minion',
        mana_cost=15,
        consider_for='Summoning',
    ),
    'Tome of Sprouts': Weapon(
        name='Tome of Sprouts',
        min_damage=70,
        max_damage=86,
        attacks_per_second=0.6024,
        damage_type='Summoning',
        delivery='Minion',
        mana_cost=15,
        consider_for='Summoning',
    ),
    'Tome of Decay': Weapon(
        name='Tome of Decay',
        min_damage=51,
        max_damage=63,
        attacks_per_second=2.0,
        damage_type='Summoning',
        delivery='Minion',
        mana_cost=15,
        aura_damage=28.5,
        consider_for='Summoning',
    ),
    'Tome of the Dark': Weapon(
        name='Tome of the Dark',
        min_damage=78,
        max_damage=96,
        attacks_per_second=0.6024,
        damage_type='Summoning',
        delivery='Minion',
        mana_cost=15,
        consider_for='Summoning',
    ),
    'Grenade': Weapon(
        name='Grenade',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=1303,
        consider_for='Explosives',
        has_durability=False,
    ),
    'Fire Grenade': Weapon(
        name='Fire Grenade',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=1303,
        consider_for='Explosives',
        attributes={
            '%_napalm_chance': 1.54,
        },
        has_durability=False,
    ),
    'Poison Grenade': Weapon(
        name='Poison Grenade',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=1303,
        consider_for='Explosives',
        attributes={
            '%_chance_to_apply_poison': 1.39,
        },
        has_durability=False,
    ),
    # Not modeled: ChanceOnHitToStun
    'Stun Grenade': Weapon(
        name='Stun Grenade',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=814,
        consider_for='Explosives',
        has_durability=False,
    ),
    'Oil Grenade': Weapon(
        name='Oil Grenade',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=977,
        consider_for='Explosives',
        has_durability=False,
    ),
    'Blast Bundle': Weapon(
        name='Blast Bundle',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=1303,
        consider_for='Explosives',
        has_durability=False,
    ),
    # Not modeled: ChanceToApplyCharmed
    'Charm Grenade': Weapon(
        name='Charm Grenade',
        min_damage=0,
        max_damage=0,
        attacks_per_second=0.6667,
        damage_type='Explosives',
        explosive_damage=33,
        consider_for='Explosives',
        has_durability=False,
    ),
}

HELMS = {
    'Hivebone Helm': Item(
        name='Hivebone Helm',
        item_category='Helm',
        set='HiveBoneSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.071,
            '+_thorns_damage': 26.0,
            '+_max_health': 45.0,
        },
    ),
    'Slime Helm': Item(
        name='Slime Helm',
        item_category='Helm',
        set='MorphaSet',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.08,
            '+_max_health': 49.0,
        },
    ),
    # Not modeled: IncreasedChanceForHigherRarityFish
    'Diving Helm': Item(
        name='Diving Helm',
        item_category='Helm',
        set='DiverSet',
        consider_for='Range',
        attributes={
            '+_fishing': 62.0,
            '+_max_health': 46.0,
        },
    ),
    'Scarab Visor': Item(
        name='Scarab Visor',
        item_category='Helm',
        set='ScarabSet',
        consider_for='Both',
        attributes={
            '+_thorns_damage': 33.0,
            '+_max_health': 45.0,
        },
    ),
    'Omoroth\'s Helm': Item(
        name='Omoroth\'s Helm',
        item_category='Helm',
        set='OctopusSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.082,
            '%_melee_and_range_attack_speed': 0.069,
            '+_max_health': 52.0,
        },
    ),
    'Miner\'s Protective Helm': Item(
        name='Miner\'s Protective Helm',
        item_category='Helm',
        set='MinerSet',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.18,
            '+_max_health': 50.0,
        },
    ),
    'Cosmos Visor Helm': Item(
        name='Cosmos Visor Helm',
        item_category='Helm',
        set='AlienTechSet',
        consider_for='Melee',
        attributes={
            '%_damage': 0.117,
            '+_mining_damage': 90.0,
            '+_max_health': 50.0,
        },
    ),
    'Atlantean Worm Helmet': Item(
        name='Atlantean Worm Helmet',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.187,
            '%_critical_hit_damage': 0.21,
            '%_critical_hit_chance': 0.07,
            '+_max_health': 46.0,
        },
    ),
    'Core Commander Helm': Item(
        name='Core Commander Helm',
        item_category='Helm',
        set='CoreCommanderSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.074,
            '%_melee_and_range_attack_speed': 0.082,
            '%_critical_hit_chance': 0.04,
            '+_max_health': 52.0,
        },
    ),
    'Shadow Helmet': Item(
        name='Shadow Helmet',
        item_category='Helm',
        set='ShadowSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.12,
            '%_critical_hit_chance': 0.04,
            '+_max_health': 44.0,
        },
    ),
    'Radical Rabbit Ears': Item(
        name='Radical Rabbit Ears',
        item_category='Helm',
        set='EasterSet',
        consider_for='Both',
        attributes={
            '+_max_health': 46.0,
        },
    ),
    'Radical Rabbit Headband': Item(
        name='Radical Rabbit Headband',
        item_category='Helm',
        set='EasterSet',
        consider_for='Both',
        attributes={
            '+_max_health': 47.0,
        },
    ),
    'Solarite Barbute': Item(
        name='Solarite Barbute',
        item_category='Helm',
        set='CrystalSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.17,
            '+_max_health': 45.0,
        },
    ),
    'Galaxite Helm': Item(
        name='Galaxite Helm',
        item_category='Helm',
        set='GalaxiteSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.19,
            '+_max_health': 49.0,
        },
    ),
    'Pandorium Helm': Item(
        name='Pandorium Helm',
        item_category='Helm',
        set='PandoriumSet',
        consider_for='Melee',
        attributes={
            '+_max_health': 54.0,
        },
    ),
    'Dreamer Headband': Item(
        name='Dreamer Headband',
        item_category='Helm',
        set='DreamerSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.087,
            '+_max_health': 46.0,
        },
    ),
    'Hunter Hood': Item(
        name='Hunter Hood',
        item_category='Helm',
        set='HunterSet',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.169,
            '+_max_health': 46.0,
        },
    ),
    'Scarlet Helm': Item(
        name='Scarlet Helm',
        item_category='Helm',
        set='ScarletArmorSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.07,
            '+_max_health': 51.0,
        },
    ),
    'Assassin Hood': Item(
        name='Assassin Hood',
        item_category='Helm',
        set='AssassinSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.112,
            '+_max_health': 51.0,
        },
    ),
    'Welder Helmet': Item(
        name='Welder Helmet',
        item_category='Helm',
        set='PlateSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.065,
            '%_damage_against_burning': 0.07,
            '+_max_health': 51.0,
        },
    ),
    'Arcane Monk Blindfold': Item(
        name='Arcane Monk Blindfold',
        item_category='Helm',
        set='MageHighSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.15,
            '%_magic_damage': 0.129,
            '+_max_mana': 66.0,
            '+_max_health': 67.0,
        },
    ),
    'Bronze Helm': Item(
        name='Bronze Helm',
        item_category='Helm',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.17,
            '+_max_health': 50.0,
        },
    ),
    'Caveling Hood': Item(
        name='Caveling Hood',
        item_category='Helm',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.183,
            '+_max_health': 43.0,
        },
    ),
    # Not modeled: DrainLessHunger
    'Cooking Pot Lid': Item(
        name='Cooking Pot Lid',
        item_category='Helm',
        set='CookingPotSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.07,
        },
    ),
    'Tassel Earrings': Item(
        name='Tassel Earrings',
        item_category='Helm',
        set='DancerSet',
        consider_for='Both',
        attributes={
            '%_physical_range_damage': 0.105,
            '%_critical_hit_damage': 0.14,
            '+_max_health': 43.0,
        },
    ),
    'Paladin Mask': Item(
        name='Paladin Mask',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.07,
        },
    ),
    'Adventurer\'s Hat': Item(
        name='Adventurer\'s Hat',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_damage': 0.194,
            '+_fishing': 70.0,
            '+_mining_damage': 154.0,
            '+_max_health': 47.0,
        },
    ),
    'Gingerbread Hood': Item(
        name='Gingerbread Hood',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.065,
            '+_max_health': 48.0,
        },
    ),
    # Not modeled: AdditionalChanceOnHitToSpawnScarabBossProjectile
    'Godsent King Mask': Item(
        name='Godsent King Mask',
        item_category='Helm',
        set='Godsent',
        consider_for='Both',
        attributes={
            '%_damage': 0.104,
            '+_max_health': 47.0,
        },
    ),
    # Not modeled: ChanceOnMeleeHitToStun
    'Hydra Bone Helm': Item(
        name='Hydra Bone Helm',
        item_category='Helm',
        set='HydraBoneSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.06,
            '+_max_health': 44.0,
        },
    ),
    'Iron Helm': Item(
        name='Iron Helm',
        item_category='Helm',
        set='IronArmorSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.124,
            '+_max_health': 44.0,
        },
    ),
    'King Slime Crown': Item(
        name='King Slime Crown',
        item_category='Helm',
        set='KingSlimeSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.04,
            '+_max_health': 52.0,
        },
    ),
    # Not modeled: MovementSpeedDecrease
    'Larva Helm': Item(
        name='Larva Helm',
        item_category='Helm',
        set='LarvaSuit',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 129.0,
            '+_max_health': 50.0,
        },
    ),
    'Moldweb Helm': Item(
        name='Moldweb Helm',
        item_category='Helm',
        set='MoldSet',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.086,
            '+_max_health': 47.0,
        },
    ),
    'Ninja Cowl': Item(
        name='Ninja Cowl',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.22,
            '%_critical_hit_chance': 0.07,
            '+_max_health': 50.0,
        },
    ),
    # Not modeled: CheatDeath
    'Plague Mask': Item(
        name='Plague Mask',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_damage': 0.105,
            '+_max_health': 44.0,
        },
    ),
    'Pot Lid': Item(
        name='Pot Lid',
        item_category='Helm',
        set='PotSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.17,
            '%_critical_hit_chance': 0.07,
        },
    ),
    'Hazmat Helm': Item(
        name='Hazmat Helm',
        item_category='Helm',
        set='RadiationSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.168,
            '+_max_health': 49.0,
        },
    ),
    'Mercenary Headband': Item(
        name='Mercenary Headband',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '%_damage': 0.11,
            '+_max_health': 25.0,
        },
    ),
    'Ranger Hood': Item(
        name='Ranger Hood',
        item_category='Helm',
        set='RangerSet',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.178,
            '+_max_health': 53.0,
        },
    ),
    'Skirmisher Cap': Item(
        name='Skirmisher Cap',
        item_category='Helm',
        set='SkirmisherSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.1,
            '+_max_health': 49.0,
        },
    ),
    'Void-Fused Helmet': Item(
        name='Void-Fused Helmet',
        item_category='Helm',
        set='VoidFusedSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.239,
            '+_max_health': 44.0,
        },
    ),
    'Warrior Helmet': Item(
        name='Warrior Helmet',
        item_category='Helm',
        set='WarriorSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.178,
            '+_max_health': 51.0,
        },
    ),
    'Lily Pad Hat': Item(
        name='Lily Pad Hat',
        item_category='Helm',
        set='SwampMageSet',
        consider_for='Both',
        attributes={
            '%_chance_to_apply_poison': 0.11,
            '+_mana_regen': 7.4,
            '+_max_health': 51.0,
            '+_magic_barrier': 58.0,
        },
    ),
    # Not modeled: ReducedDamageFromBosses
    'Sentry Helm': Item(
        name='Sentry Helm',
        item_category='Helm',
        set='GolemSet',
        consider_for='Both',
        attributes={
            '+_max_health': 51.0,
        },
    ),
    'Octarine Helm': Item(
        name='Octarine Helm',
        item_category='Helm',
        set='OctarineSet',
        consider_for='Both',
        attributes={
            '+_max_health': 48.0,
        },
    ),
    'Carapace Helm': Item(
        name='Carapace Helm',
        item_category='Helm',
        set='CarapaceArmorSet',
        consider_for='Both',
        attributes={
            '+_max_health': 44.0,
            '%_explosives_damage': 0.15,
        },
    ),
    'Magma Horn Armor': Item(
        name='Magma Horn Armor',
        item_category='Helm',
        set='LavaSet',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 30.0,
            '+_max_health': 46.0,
        },
    ),
    # Not modeled: ChanceToConsumeBurning
    'Shaman Skull': Item(
        name='Shaman Skull',
        item_category='Helm',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 21.0,
            '+_max_health': 52.0,
        },
    ),
    'Apprentice Hat': Item(
        name='Apprentice Hat',
        item_category='Helm',
        set='MageLowSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.153,
            '+_max_health': 53.0,
            '+_magic_barrier': 84.0,
        },
    ),
    'Chieftain Headdress': Item(
        name='Chieftain Headdress',
        item_category='Helm',
        set='ChieftainSet',
        consider_for='Magic',
        attributes={
            '%_minion_damage': 0.204,
            '%_mana_reservation_reduction': 0.26,
            '+_max_health': 50.0,
            '+_magic_barrier': 78.0,
        },
    ),
    'Corrupt Warden Mask': Item(
        name='Corrupt Warden Mask',
        item_category='Helm',
        set='SummonerMidSet',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 6.4,
            '+_max_minions': 1.0,
            '%_mana_reservation_reduction': 0.43,
            '+_max_health': 76.0,
        },
    ),
    'Grim Hood': Item(
        name='Grim Hood',
        item_category='Helm',
        set='SummonerHighSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.084,
            '%_minion_damage': 0.073,
            '+_max_minions': 2.0,
            '+_max_health': 53.0,
            '+_magic_barrier': 33.0,
        },
    ),
    'Scholar\'s Hood': Item(
        name='Scholar\'s Hood',
        item_category='Helm',
        set='ScholarSet',
        consider_for='Magic',
        attributes={
            '%_minion_attack_speed': 0.324,
            '+_max_minions': 1.0,
            '+_max_health': 49.0,
            '+_magic_barrier': 67.0,
        },
    ),
    # Not modeled: ExtraHealFromSleepPercentage
    'Pajama Cap': Item(
        name='Pajama Cap',
        item_category='Helm',
        set='SleepySet',
        consider_for='Magic',
        attributes={
            '+_max_mana': 49.0,
            '+_max_health': 52.0,
        },
    ),
    'Soaring Headgear': Item(
        name='Soaring Headgear',
        item_category='Helm',
        set='SoaringSet',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 5.7,
            '+_max_health': 49.0,
            '+_magic_barrier': 73.0,
        },
    ),
    'Sorcerer Hood': Item(
        name='Sorcerer Hood',
        item_category='Helm',
        set='MageMidSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.231,
            '+_max_mana': 67.0,
            '+_max_health': 71.0,
            '+_magic_barrier': 93.0,
        },
    ),
    'Desert Guardian Mask': Item(
        name='Desert Guardian Mask',
        item_category='Helm',
        set='DesertGuardianSet',
        consider_for='Both',
        attributes={
            '%_minion_attack_speed': 0.256,
            '+_max_minions': 1.0,
            '%_mana_reservation_reduction': 0.19,
            '+_max_health': 48.0,
        },
    ),
    'Witch Doctor Hat': Item(
        name='Witch Doctor Hat',
        item_category='Helm',
        set='SummonerLowSet',
        consider_for='Both',
        attributes={
            '+_max_minions': 1.0,
            '%_mana_reservation_reduction': 0.25,
            '+_max_health': 50.0,
        },
    ),
}

BREAST_ARMORS = {
    'Hunter Cloak': Item(
        name='Hunter Cloak',
        item_category='Breast armor',
        set='HunterSet',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.216,
            '+_max_health': 72.0,
        },
    ),
    'Slime Armor': Item(
        name='Slime Armor',
        item_category='Breast armor',
        set='MorphaSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.255,
            '+_max_health': 61.0,
        },
    ),
    'Hivebone Breastplate': Item(
        name='Hivebone Breastplate',
        item_category='Breast armor',
        set='HiveBoneSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.104,
            '+_thorns_damage': 23.0,
            '+_max_health': 65.0,
        },
    ),
    'Ivy\'s Thorn Harness': Item(
        name='Ivy\'s Thorn Harness',
        item_category='Breast armor',
        set='IvySet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.5,
            '+_max_health': 97.0,
        },
    ),
    'Miner\'s Labor Suit': Item(
        name='Miner\'s Labor Suit',
        item_category='Breast armor',
        set='MinerSet',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.24,
            '+_max_health': 62.0,
        },
    ),
    'Cosmos Torso': Item(
        name='Cosmos Torso',
        item_category='Breast armor',
        set='AlienTechSet',
        consider_for='Melee',
        attributes={
            '%_damage': 0.121,
            '+_mining_damage': 106.0,
            '+_max_health': 68.0,
        },
    ),
    'Scarab Harness': Item(
        name='Scarab Harness',
        item_category='Breast armor',
        set='ScarabSet',
        consider_for='Both',
        attributes={
            '+_thorns_damage': 42.0,
            '+_max_health': 69.0,
        },
    ),
    'Omoroth\'s Chestplate': Item(
        name='Omoroth\'s Chestplate',
        item_category='Breast armor',
        set='OctopusSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.106,
            '%_melee_and_range_attack_speed': 0.09,
            '+_max_health': 63.0,
        },
    ),
    'Core Commander Brigandine': Item(
        name='Core Commander Brigandine',
        item_category='Breast armor',
        set='CoreCommanderSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.076,
            '%_melee_and_range_attack_speed': 0.105,
            '%_critical_hit_damage': 0.11,
            '+_max_health': 66.0,
        },
    ),
    'Shadow Chestplate': Item(
        name='Shadow Chestplate',
        item_category='Breast armor',
        set='ShadowSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.125,
            '%_melee_and_range_attack_speed': 0.1,
            '+_max_health': 70.0,
        },
    ),
    # Not modeled: ChanceToPreserveBait
    'Kelp Mantle': Item(
        name='Kelp Mantle',
        item_category='Breast armor',
        set='DiverSet',
        consider_for='Range',
        attributes={
            '+_max_health': 64.0,
        },
    ),
    'Solarite Cuirass': Item(
        name='Solarite Cuirass',
        item_category='Breast armor',
        set='CrystalSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.094,
            '+_max_health': 65.0,
        },
    ),
    'Galaxite Torso': Item(
        name='Galaxite Torso',
        item_category='Breast armor',
        set='GalaxiteSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.25,
            '+_max_health': 61.0,
        },
    ),
    'Pandorium Chestplate and Bracers': Item(
        name='Pandorium Chestplate and Bracers',
        item_category='Breast armor',
        set='PandoriumSet',
        consider_for='Melee',
        attributes={
            '+_max_health': 60.0,
        },
    ),
    'Dreamer Vest': Item(
        name='Dreamer Vest',
        item_category='Breast armor',
        set='DreamerSet',
        consider_for='Range',
        attributes={
            '%_range_damage': 0.213,
            '+_max_health': 67.0,
        },
    ),
    'Scarlet Breastplate': Item(
        name='Scarlet Breastplate',
        item_category='Breast armor',
        set='ScarletArmorSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.1,
            '+_max_health': 62.0,
        },
    ),
    'Assassin Cloak': Item(
        name='Assassin Cloak',
        item_category='Breast armor',
        set='AssassinSet',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.121,
            '+_max_health': 70.0,
        },
    ),
    'Welder Chestplate': Item(
        name='Welder Chestplate',
        item_category='Breast armor',
        set='PlateSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.06,
            '%_damage_against_burning': 0.1,
            '+_max_health': 62.0,
        },
    ),
    'Gemstone Garment': Item(
        name='Gemstone Garment',
        item_category='Breast armor',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.067,
            '%_range_attack_speed': 0.192,
            '+_max_health': 65.0,
        },
    ),
    'Arcane Monk Cloak': Item(
        name='Arcane Monk Cloak',
        item_category='Breast armor',
        set='MageHighSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.19,
            '%_magic_damage': 0.155,
            '+_max_mana': 64.0,
            '+_max_health': 65.0,
        },
    ),
    'Bronze Breastplate': Item(
        name='Bronze Breastplate',
        item_category='Breast armor',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.244,
            '+_max_health': 72.0,
        },
    ),
    'Caveling Chest': Item(
        name='Caveling Chest',
        item_category='Breast armor',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.206,
            '+_max_health': 67.0,
        },
    ),
    # Not modeled: DrainLessHunger
    'Cooking Pot Tub': Item(
        name='Cooking Pot Tub',
        item_category='Breast armor',
        set='CookingPotSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.06,
        },
    ),
    'Cupid Tunic': Item(
        name='Cupid Tunic',
        item_category='Breast armor',
        set='CupidSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.107,
            '+_max_health': 72.0,
        },
    ),
    'Tassel Top': Item(
        name='Tassel Top',
        item_category='Breast armor',
        set='DancerSet',
        consider_for='Both',
        attributes={
            '%_range_attack_speed': 0.104,
            '%_critical_hit_chance': 0.07,
            '+_max_health': 72.0,
        },
    ),
    'Paladin Harness': Item(
        name='Paladin Harness',
        item_category='Breast armor',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.09,
        },
    ),
    # Not modeled: AdditionalChanceOnCritToSpawnThunderBeam
    'Godsent King Breast Armor': Item(
        name='Godsent King Breast Armor',
        item_category='Breast armor',
        set='Godsent',
        consider_for='Both',
        attributes={
            '%_damage': 0.118,
            '+_max_health': 63.0,
        },
    ),
    # Not modeled: ChanceOnMeleeHitToStun
    'Hydra Bone Breastplate': Item(
        name='Hydra Bone Breastplate',
        item_category='Breast armor',
        set='HydraBoneSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.141,
            '+_max_health': 69.0,
        },
    ),
    'Iron Breastplate': Item(
        name='Iron Breastplate',
        item_category='Breast armor',
        set='IronArmorSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.184,
            '+_max_health': 72.0,
        },
    ),
    # Not modeled: MovementSpeedDecrease
    'Larva Chest': Item(
        name='Larva Chest',
        item_category='Breast armor',
        set='LarvaSuit',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 135.0,
            '+_max_health': 68.0,
        },
    ),
    'Moldweb Breastplate': Item(
        name='Moldweb Breastplate',
        item_category='Breast armor',
        set='MoldSet',
        consider_for='Both',
        attributes={
            '%_physical_melee_damage': 0.146,
            '%_damage_against_bosses': 0.16,
            '+_max_health': 65.0,
        },
    ),
    'Ninja Garments': Item(
        name='Ninja Garments',
        item_category='Breast armor',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.22,
            '%_critical_hit_chance': 0.09,
            '+_max_health': 68.0,
        },
    ),
    'Octarine Breastplate': Item(
        name='Octarine Breastplate',
        item_category='Breast armor',
        set='OctarineSet',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.11,
            '+_max_health': 61.0,
        },
    ),
    'Pot Tub': Item(
        name='Pot Tub',
        item_category='Breast armor',
        set='PotSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.19,
            '%_critical_hit_chance': 0.06,
        },
    ),
    'Hazmat Suit Jacket': Item(
        name='Hazmat Suit Jacket',
        item_category='Breast armor',
        set='RadiationSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.217,
            '+_max_health': 69.0,
        },
    ),
    # Not modeled: MovementSpeedBoostAfterDodge
    'Mercenary Tank Top': Item(
        name='Mercenary Tank Top',
        item_category='Breast armor',
        consider_for='Both',
        attributes={
            '%_damage': 0.174,
            '+_max_health': 68.0,
        },
    ),
    'Ranger Tunic': Item(
        name='Ranger Tunic',
        item_category='Breast armor',
        set='RangerSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.113,
            '+_max_health': 67.0,
        },
    ),
    'Skirmisher Harness': Item(
        name='Skirmisher Harness',
        item_category='Breast armor',
        set='SkirmisherSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.107,
            '+_max_health': 68.0,
        },
    ),
    'Soaring Poncho': Item(
        name='Soaring Poncho',
        item_category='Breast armor',
        set='SoaringSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.1,
            '+_max_health': 69.0,
            '+_magic_barrier': 116.0,
        },
    ),
    'Void-Fused Chestpiece': Item(
        name='Void-Fused Chestpiece',
        item_category='Breast armor',
        set='VoidFusedSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.257,
            '+_max_health': 67.0,
        },
    ),
    'Warrior Chestplate': Item(
        name='Warrior Chestplate',
        item_category='Breast armor',
        set='WarriorSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.218,
            '+_max_health': 69.0,
        },
    ),
    'Lily Pad Tunic': Item(
        name='Lily Pad Tunic',
        item_category='Breast armor',
        set='SwampMageSet',
        consider_for='Both',
        attributes={
            '%_chance_to_apply_poison': 0.13,
            '+_max_mana': 63.0,
            '+_max_health': 65.0,
            '+_magic_barrier': 84.0,
        },
    ),
    # Not modeled: ReducedDamageFromBosses
    'Stone Chestplate': Item(
        name='Stone Chestplate',
        item_category='Breast armor',
        set='GolemSet',
        consider_for='Both',
        attributes={
            '+_max_health': 72.0,
        },
    ),
    'Carapace Breastplate': Item(
        name='Carapace Breastplate',
        item_category='Breast armor',
        set='CarapaceArmorSet',
        consider_for='Both',
        attributes={
            '+_max_health': 68.0,
            '%_explosives_damage': 0.21,
        },
    ),
    'Magma Torso Armor': Item(
        name='Magma Torso Armor',
        item_category='Breast armor',
        set='LavaSet',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 40.0,
            '+_max_health': 65.0,
        },
    ),
    'Apprentice Robe': Item(
        name='Apprentice Robe',
        item_category='Breast armor',
        set='MageLowSet',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 7.6,
            '+_max_health': 60.0,
            '+_magic_barrier': 101.0,
        },
    ),
    'Chieftain Tunic': Item(
        name='Chieftain Tunic',
        item_category='Breast armor',
        set='ChieftainSet',
        consider_for='Magic',
        attributes={
            '+_max_minions': 1.0,
            '+_max_health': 61.0,
            '+_magic_barrier': 43.0,
        },
    ),
    'Corrupt Warden Tunic': Item(
        name='Corrupt Warden Tunic',
        item_category='Breast armor',
        set='SummonerMidSet',
        consider_for='Magic',
        attributes={
            '+_max_mana': 64.0,
            '%_minion_damage': 0.193,
            '+_max_minions': 1.0,
            '+_max_health': 90.0,
        },
    ),
    'Grim Breastplate': Item(
        name='Grim Breastplate',
        item_category='Breast armor',
        set='SummonerHighSet',
        consider_for='Magic',
        attributes={
            '+_max_mana': 62.0,
            '+_max_minions': 1.0,
            '%_mana_reservation_reduction': 0.25,
            '+_max_health': 68.0,
            '+_magic_barrier': 51.0,
        },
    ),
    'Scholar\'s Cloak': Item(
        name='Scholar\'s Cloak',
        item_category='Breast armor',
        set='ScholarSet',
        consider_for='Magic',
        attributes={
            '+_max_mana': 62.0,
            '+_max_minions': 1.0,
            '+_max_health': 70.0,
            '+_magic_barrier': 92.0,
        },
    ),
    'Pajama Shirt': Item(
        name='Pajama Shirt',
        item_category='Breast armor',
        set='SleepySet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.402,
            '+_max_mana': 62.0,
            '+_max_health': 72.0,
        },
    ),
    'Sorcerer Robe': Item(
        name='Sorcerer Robe',
        item_category='Breast armor',
        set='MageMidSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.206,
            '+_max_mana': 68.0,
            '+_max_health': 61.0,
            '+_magic_barrier': 93.0,
        },
    ),
    'Desert Guardian Tunic': Item(
        name='Desert Guardian Tunic',
        item_category='Breast armor',
        set='DesertGuardianSet',
        consider_for='Both',
        attributes={
            '+_max_minions': 1.0,
            '+_max_health': 62.0,
        },
    ),
    'Witch Doctor Vest': Item(
        name='Witch Doctor Vest',
        item_category='Breast armor',
        set='SummonerLowSet',
        consider_for='Both',
        attributes={
            '+_max_minions': 1.0,
            '+_max_health': 72.0,
        },
    ),
}

PANTS_ARMORS = {
    'Bronze Pants': Item(
        name='Bronze Pants',
        item_category='Pants armor',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.198,
            '+_max_health': 58.0,
        },
    ),
    'Iron Pants': Item(
        name='Iron Pants',
        item_category='Pants armor',
        set='IronArmorSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.149,
            '+_max_health': 56.0,
        },
    ),
    'Miner\'s Worker Pants': Item(
        name='Miner\'s Worker Pants',
        item_category='Pants armor',
        set='MinerSet',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 131.0,
            '+_max_health': 65.0,
        },
    ),
    'Cosmos Legwear': Item(
        name='Cosmos Legwear',
        item_category='Pants armor',
        set='AlienTechSet',
        consider_for='Melee',
        attributes={
            '%_damage': 0.124,
            '+_mining_damage': 94.0,
            '+_max_health': 62.0,
        },
    ),
    'Scarab Legs': Item(
        name='Scarab Legs',
        item_category='Pants armor',
        set='ScarabSet',
        consider_for='Both',
        attributes={
            '+_thorns_damage': 39.0,
            '+_max_health': 56.0,
        },
    ),
    'Omoroth\'s Leg Armor': Item(
        name='Omoroth\'s Leg Armor',
        item_category='Pants armor',
        set='OctopusSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.097,
            '%_melee_and_range_attack_speed': 0.084,
            '+_max_health': 56.0,
        },
    ),
    'Hivebone Pants': Item(
        name='Hivebone Pants',
        item_category='Pants armor',
        set='HiveBoneSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.093,
            '+_thorns_damage': 22.0,
            '+_max_health': 57.0,
        },
    ),
    'Ivy\'s Pants': Item(
        name='Ivy\'s Pants',
        item_category='Pants armor',
        set='IvySet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.49,
            '+_max_health': 89.0,
        },
    ),
    'Core Commander Greaves': Item(
        name='Core Commander Greaves',
        item_category='Pants armor',
        set='CoreCommanderSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.09,
            '%_critical_hit_damage': 0.12,
            '%_critical_hit_chance': 0.04,
            '+_max_health': 58.0,
        },
    ),
    'Shadow Leggings': Item(
        name='Shadow Leggings',
        item_category='Pants armor',
        set='ShadowSet',
        consider_for='Both',
        attributes={
            '+_max_health': 59.0,
        },
    ),
    # Not modeled: IncreasedChanceToGetFish
    'Scuba Fins': Item(
        name='Scuba Fins',
        item_category='Pants armor',
        set='DiverSet',
        consider_for='Range',
        attributes={
            '+_max_health': 58.0,
        },
    ),
    'Solarite Tassets': Item(
        name='Solarite Tassets',
        item_category='Pants armor',
        set='CrystalSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.09,
            '+_max_health': 64.0,
        },
    ),
    'Galaxite Pants': Item(
        name='Galaxite Pants',
        item_category='Pants armor',
        set='GalaxiteSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.25,
            '+_max_health': 62.0,
        },
    ),
    'Pandorium Pants': Item(
        name='Pandorium Pants',
        item_category='Pants armor',
        set='PandoriumSet',
        consider_for='Melee',
        attributes={
            '+_max_health': 57.0,
        },
    ),
    'Dreamer Shalvar': Item(
        name='Dreamer Shalvar',
        item_category='Pants armor',
        set='DreamerSet',
        consider_for='Range',
        attributes={
            '%_critical_hit_chance': 0.08,
            '+_max_health': 61.0,
        },
    ),
    'Scarlet Pants': Item(
        name='Scarlet Pants',
        item_category='Pants armor',
        set='ScarletArmorSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.08,
            '+_max_health': 54.0,
        },
    ),
    'Welder Leggings': Item(
        name='Welder Leggings',
        item_category='Pants armor',
        set='PlateSet',
        consider_for='Both',
        attributes={
            '%_damage_against_burning': 0.08,
            '%_critical_hit_damage_against_burning': 0.13,
            '+_max_health': 64.0,
        },
    ),
    'Gemstone Harem Pants': Item(
        name='Gemstone Harem Pants',
        item_category='Pants armor',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.091,
            '+_max_health': 55.0,
        },
    ),
    'Arcane Monk Leggings': Item(
        name='Arcane Monk Leggings',
        item_category='Pants armor',
        set='MageHighSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.06,
            '%_magic_damage': 0.13,
            '+_mana_regen': 8.2,
            '+_max_health': 63.0,
        },
    ),
    'Caveling Pants': Item(
        name='Caveling Pants',
        item_category='Pants armor',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.21,
            '+_max_health': 56.0,
        },
    ),
    'Tassel Skirt': Item(
        name='Tassel Skirt',
        item_category='Pants armor',
        set='DancerSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.093,
            '+_max_health': 60.0,
        },
    ),
    'Paladin Pants': Item(
        name='Paladin Pants',
        item_category='Pants armor',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.08,
        },
    ),
    # Not modeled: AdditionalChanceOnRangeHitToSpawnOctopusBossProjectile
    'Godsent King Pants Armor': Item(
        name='Godsent King Pants Armor',
        item_category='Pants armor',
        set='Godsent',
        consider_for='Both',
        attributes={
            '%_damage': 0.11,
            '+_max_health': 58.0,
        },
    ),
    # Not modeled: ChanceOnMeleeHitToStun
    'Hydra Bone Shins': Item(
        name='Hydra Bone Shins',
        item_category='Pants armor',
        set='HydraBoneSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.083,
            '+_max_health': 66.0,
        },
    ),
    'Moldweb Pants': Item(
        name='Moldweb Pants',
        item_category='Pants armor',
        set='MoldSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.194,
            '+_max_health': 65.0,
        },
    ),
    'Ninja Leggings': Item(
        name='Ninja Leggings',
        item_category='Pants armor',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.25,
            '%_critical_hit_chance': 0.08,
            '+_max_health': 57.0,
        },
    ),
    'Octarine Pants': Item(
        name='Octarine Pants',
        item_category='Pants armor',
        set='OctarineSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.093,
            '+_max_health': 54.0,
        },
    ),
    'Hazmat Suit Pants': Item(
        name='Hazmat Suit Pants',
        item_category='Pants armor',
        set='RadiationSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.232,
            '+_max_health': 55.0,
        },
    ),
    'Mercenary Pants': Item(
        name='Mercenary Pants',
        item_category='Pants armor',
        consider_for='Both',
        attributes={
            '%_damage': 0.217,
            '+_max_health': 33.0,
        },
    ),
    'Ranger Pants': Item(
        name='Ranger Pants',
        item_category='Pants armor',
        set='RangerSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.23,
            '+_max_health': 59.0,
        },
    ),
    'Void-Fused Leggings': Item(
        name='Void-Fused Leggings',
        item_category='Pants armor',
        set='VoidFusedSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.218,
            '+_max_health': 64.0,
        },
    ),
    'Warrior Greaves': Item(
        name='Warrior Greaves',
        item_category='Pants armor',
        set='WarriorSet',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.204,
            '+_max_health': 60.0,
        },
    ),
    'Lily Pad Shorts': Item(
        name='Lily Pad Shorts',
        item_category='Pants armor',
        set='SwampMageSet',
        consider_for='Both',
        attributes={
            '%_chance_to_apply_poison': 0.09,
            '+_max_health': 58.0,
            '+_magic_barrier': 83.0,
            '%_barrier_as_magic_damage': 0.06,
        },
    ),
    # Not modeled: ReducedDamageFromBosses
    'Stone Pants': Item(
        name='Stone Pants',
        item_category='Pants armor',
        set='GolemSet',
        consider_for='Both',
        attributes={
            '+_max_health': 61.0,
        },
    ),
    'Magma Shin Armor': Item(
        name='Magma Shin Armor',
        item_category='Pants armor',
        set='LavaSet',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 38.0,
            '+_max_health': 59.0,
        },
    ),
    'Apprentice Pants': Item(
        name='Apprentice Pants',
        item_category='Pants armor',
        set='MageLowSet',
        consider_for='Magic',
        attributes={
            '+_max_mana': 62.0,
            '+_max_health': 63.0,
            '+_magic_barrier': 104.0,
        },
    ),
    'Chieftain Shorts': Item(
        name='Chieftain Shorts',
        item_category='Pants armor',
        set='ChieftainSet',
        consider_for='Magic',
        attributes={
            '%_minion_attack_speed': 0.461,
            '+_max_health': 58.0,
            '+_magic_barrier': 39.0,
        },
    ),
    'Corrupt Warden Shorts': Item(
        name='Corrupt Warden Shorts',
        item_category='Pants armor',
        set='SummonerMidSet',
        consider_for='Magic',
        attributes={
            '+_max_mana': 59.0,
            '%_minion_damage': 0.18,
            '+_max_minions': 1.0,
            '+_max_health': 85.0,
        },
    ),
    'Grim Legwear': Item(
        name='Grim Legwear',
        item_category='Pants armor',
        set='SummonerHighSet',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 7.6,
            '%_minion_damage': 0.14,
            '+_max_minions': 1.0,
            '+_max_health': 58.0,
            '+_magic_barrier': 44.0,
        },
    ),
    'Pajama Pants': Item(
        name='Pajama Pants',
        item_category='Pants armor',
        set='SleepySet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.42,
            '+_max_mana': 56.0,
            '+_max_health': 59.0,
        },
    ),
    'Soaring Pants': Item(
        name='Soaring Pants',
        item_category='Pants armor',
        set='SoaringSet',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 7.3,
            '+_max_health': 65.0,
            '+_magic_barrier': 103.0,
        },
    ),
    'Sorcerer Pants': Item(
        name='Sorcerer Pants',
        item_category='Pants armor',
        set='MageMidSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.232,
            '+_max_mana': 66.0,
            '+_max_health': 60.0,
            '+_magic_barrier': 89.0,
        },
    ),
    'Desert Guardian Pants': Item(
        name='Desert Guardian Pants',
        item_category='Pants armor',
        set='DesertGuardianSet',
        consider_for='Both',
        attributes={
            '%_minion_critical_hit_chance': 0.06,
            '+_max_minions': 1.0,
            '+_max_health': 61.0,
        },
    ),
    'Witch Doctor Jeans': Item(
        name='Witch Doctor Jeans',
        item_category='Pants armor',
        set='SummonerLowSet',
        consider_for='Both',
        attributes={
            '+_max_health': 63.0,
        },
    ),
}

NECKLACES = {
    'Polished Copper Cross Necklace': Item(
        name='Polished Copper Cross Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.26,
            '%_critical_hit_chance': 0.09,
        },
    ),
    'Polished Octarine Necklace': Item(
        name='Polished Octarine Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.11,
        },
    ),
    'Neptune Necklace': Item(
        name='Neptune Necklace',
        item_category='Necklace',
        set='DiverSet',
        consider_for='Range',
        attributes={
            '+_fishing': 133.0,
        },
    ),
    'Mold Vein Necklace': Item(
        name='Mold Vein Necklace',
        item_category='Necklace',
        set='MoldRingAndNecklace',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.408,
        },
    ),
    'Torc Necklace': Item(
        name='Torc Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_damage': 0.261,
        },
    ),
    'Rusted Necklace': Item(
        name='Rusted Necklace',
        item_category='Necklace',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.37,
        },
    ),
    'Black Necklace': Item(
        name='Black Necklace',
        item_category='Necklace',
        set='MinerSet',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 118.0,
        },
    ),
    'Ancient Gem Necklace': Item(
        name='Ancient Gem Necklace',
        item_category='Necklace',
        set='AncientGemRingAndNecklace',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.051,
        },
    ),
    'Tower Shell Necklace': Item(
        name='Tower Shell Necklace',
        item_category='Necklace',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 253.0,
        },
    ),
    'Ra-Akar\'s Necklace': Item(
        name='Ra-Akar\'s Necklace',
        item_category='Necklace',
        set='ScarabSet',
        consider_for='Both',
        attributes={
            '+_thorns_damage': 20.0,
            '+_max_health': 32.0,
        },
    ),
    # Not modeled: IncreasedDamageTakenPercentage
    'Glass Bead Necklace': Item(
        name='Glass Bead Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.85,
        },
    ),
    # Not modeled: ExtraHarvestChance
    'Eostre Necklace': Item(
        name='Eostre Necklace',
        item_category='Necklace',
        set='EasterSet',
        consider_for='Both',
    ),
    'Blob Rosary Necklace': Item(
        name='Blob Rosary Necklace',
        item_category='Necklace',
        set='SlimeRingAndNecklace',
        consider_for='Range',
        attributes={
            '+_max_health': 62.0,
        },
    ),
    'Atlantean Worm Necklace': Item(
        name='Atlantean Worm Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_damage_against_bosses': 0.2,
        },
    ),
    'Azeos Beak Necklace': Item(
        name='Azeos Beak Necklace',
        item_category='Necklace',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 118.0,
        },
    ),
    'Azure Necklace': Item(
        name='Azure Necklace',
        item_category='Necklace',
        set='AzureSet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.053,
            '%_magic_damage': 0.199,
        },
    ),
    'Bone Necklace': Item(
        name='Bone Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.09,
        },
    ),
    'Chime Necklace': Item(
        name='Chime Necklace',
        item_category='Necklace',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.232,
            '%_range_damage_while_standing_still': 0.175,
        },
    ),
    'Copper Cross Necklace': Item(
        name='Copper Cross Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.18,
        },
    ),
    'Enigmatic Necklace': Item(
        name='Enigmatic Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.08,
            '%_magic_damage': 0.184,
        },
    ),
    'Fang Necklace': Item(
        name='Fang Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Grub Egg Necklace': Item(
        name='Grub Egg Necklace',
        item_category='Necklace',
        set='LarvaRingAndNecklace',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.41,
        },
    ),
    'Helio Necklace': Item(
        name='Helio Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_physical_melee_damage': 0.21,
            '%_critical_hit_damage': 0.24,
        },
    ),
    'Pyrdra\'s Necklace': Item(
        name='Pyrdra\'s Necklace',
        item_category='Necklace',
        set='HydraJewelrySet',
        consider_for='Both',
        attributes={
            '%_damage_against_burning': 0.18,
            '+_burn_damage_on_hit': 22.0,
            '+_max_health': 23.0,
        },
    ),
    'Knight\'s Necklace': Item(
        name='Knight\'s Necklace',
        item_category='Necklace',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.05,
        },
    ),
    'Moonbell Necklace': Item(
        name='Moonbell Necklace',
        item_category='Necklace',
        set='MoonbellSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.26,
            '%_magic_damage': 0.186,
        },
    ),
    'Needle Necklace': Item(
        name='Needle Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_range_attack_speed': 0.055,
            '%_critical_hit_chance': 0.09,
        },
    ),
    'Nomad Necklace': Item(
        name='Nomad Necklace',
        item_category='Necklace',
        set='NomadSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.37,
            '+_max_health': 57.0,
        },
    ),
    'Octarine Necklace': Item(
        name='Octarine Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.087,
        },
    ),
    'Omoroth\'s Necklace': Item(
        name='Omoroth\'s Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_damage': 0.105,
            '%_mining_damage': 0.15,
        },
    ),
    # Not modeled: ApplyPetCritChanceIncrease
    'Wildwarden Necklace': Item(
        name='Wildwarden Necklace',
        item_category='Necklace',
        set='TamerSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.05,
        },
    ),
    'Thorn Necklace': Item(
        name='Thorn Necklace',
        item_category='Necklace',
        consider_for='Both',
        attributes={
            '%_melee_attack_speed': 0.051,
            '+_thorns_damage': 19.0,
        },
    ),
    'Flame Necklace': Item(
        name='Flame Necklace',
        item_category='Necklace',
        set='FlameSet',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 75.0,
        },
    ),
    'Skull Necklace': Item(
        name='Skull Necklace',
        item_category='Necklace',
        set='SkullRingAndNecklace',
        consider_for='Both',
        attributes={
            '%_minion_damage': 0.772,
            '+_max_health': -57.0,
        },
    ),
    'Bombshell Necklace': Item(
        name='Bombshell Necklace',
        item_category='Necklace',
        consider_for='Magic',
        attributes={
            '%_explosives_damage': 0.18,
            '+_magic_barrier': 41.0,
        },
    ),
    'Bubble Pearl Necklace': Item(
        name='Bubble Pearl Necklace',
        item_category='Necklace',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.134,
            '+_mana_regen': 2.6,
            '+_magic_barrier': 26.0,
        },
    ),
    'Crescent Necklace': Item(
        name='Crescent Necklace',
        item_category='Necklace',
        consider_for='Magic',
        attributes={
            '+_max_mana': 63.0,
        },
    ),
    'Gold Crystal Necklace': Item(
        name='Gold Crystal Necklace',
        item_category='Necklace',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.182,
            '%_minion_damage': 0.19,
        },
    ),
    'Polished Gold Crystal Necklace': Item(
        name='Polished Gold Crystal Necklace',
        item_category='Necklace',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.282,
            '%_minion_damage': 0.299,
        },
    ),
    'Warped Necklace': Item(
        name='Warped Necklace',
        item_category='Necklace',
        set='WarpedSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.123,
            '+_max_mana': 19.0,
            '+_magic_barrier': 29.0,
        },
    ),
    'Codex Necklace': Item(
        name='Codex Necklace',
        item_category='Necklace',
        consider_for='Summoning',
        attributes={
            '%_minion_attack_speed': 0.834,
            '%_mana_reservation_reduction': 0.22,
        },
    ),
    'Orb Necklace': Item(
        name='Orb Necklace',
        item_category='Necklace',
        consider_for='Summoning',
        attributes={
            '%_minion_attack_speed': 0.459,
            '%_mana_reservation_reduction': 0.2,
        },
    ),
    'Soul Medallion': Item(
        name='Soul Medallion',
        item_category='Necklace',
        consider_for='Summoning',
        attributes={
            '%_minion_critical_hit_chance': 0.1,
            '+_max_minions': 1.0,
        },
    ),
}

RINGS = {
    'Sea Foam Ring': Item(
        name='Sea Foam Ring',
        item_category='Ring',
        consider_for='Range',
        attributes={
            '+_fishing': 113.0,
        },
    ),
    'Gold Crystal Ring': Item(
        name='Gold Crystal Ring',
        item_category='Ring',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.436,
        },
    ),
    'Ring of Stone': Item(
        name='Ring of Stone',
        item_category='Ring',
        set='RockAndStoneRings',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 276.0,
        },
    ),
    'Ancient Gem Ring': Item(
        name='Ancient Gem Ring',
        item_category='Ring',
        set='AncientGemRingAndNecklace',
        consider_for='Melee',
        attributes={
            '%_critical_hit_damage': 0.24,
            '+_mining_damage': 133.0,
        },
    ),
    'Topaz Ring': Item(
        name='Topaz Ring',
        item_category='Ring',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.41,
        },
    ),
    'Black Ring': Item(
        name='Black Ring',
        item_category='Ring',
        set='MinerSet',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 82.0,
        },
    ),
    'Polished Gold Crystal Ring': Item(
        name='Polished Gold Crystal Ring',
        item_category='Ring',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.295,
            '%_range_attack_speed': 0.054,
        },
    ),
    'Polished Golden Spike Ring': Item(
        name='Polished Golden Spike Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.31,
            '%_critical_hit_chance': 0.09,
            '+_thorns_damage': 27.0,
        },
    ),
    # Not modeled: FishBitesFaster
    'Goldfish Ring': Item(
        name='Goldfish Ring',
        item_category='Ring',
        set='DiverSet',
        consider_for='Range',
    ),
    'Druidra\'s Ring': Item(
        name='Druidra\'s Ring',
        item_category='Ring',
        set='HydraJewelrySet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.15,
            '%_chance_to_apply_poison': 0.08,
            '%_damage_against_poisoned': 0.18,
        },
    ),
    'Ivy\'s Ring': Item(
        name='Ivy\'s Ring',
        item_category='Ring',
        set='IvySet',
        consider_for='Range',
        attributes={
            '%_range_attack_speed': 0.09,
        },
    ),
    # Not modeled: IncreasedDamageTakenPercentage
    'Glass Bead Ring': Item(
        name='Glass Bead Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_damage': 0.369,
        },
    ),
    'Double Ring': Item(
        name='Double Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_damage': 0.076,
            '%_melee_and_range_attack_speed': 0.046,
            '%_critical_hit_damage': 0.11,
            '%_critical_hit_chance': 0.04,
        },
    ),
    'Morpha\'s Ring': Item(
        name='Morpha\'s Ring',
        item_category='Ring',
        set='MorphaSet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.51,
        },
    ),
    'Wooden Thorn Ring': Item(
        name='Wooden Thorn Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '+_thorns_damage': 43.0,
        },
    ),
    'Skull Ring': Item(
        name='Skull Ring',
        item_category='Ring',
        set='SkullRingAndNecklace',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.172,
            '+_max_health': -65.0,
        },
    ),
    'Ostara Ring': Item(
        name='Ostara Ring',
        item_category='Ring',
        set='EasterSet',
        consider_for='Both',
    ),
    'Melting Crystal Ring': Item(
        name='Melting Crystal Ring',
        item_category='Ring',
        set='SlimeRingAndNecklace',
        consider_for='Range',
    ),
    'Ring of Rock': Item(
        name='Ring of Rock',
        item_category='Ring',
        set='RockAndStoneRings',
        consider_for='Melee',
    ),
    'Atlantean Worm Ring': Item(
        name='Atlantean Worm Ring',
        item_category='Ring',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.2,
        },
    ),
    'Bone Ring': Item(
        name='Bone Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.09,
        },
    ),
    'Bubble Ring': Item(
        name='Bubble Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.08,
            '%_magic_damage': 0.204,
        },
    ),
    'Clarity Ring': Item(
        name='Clarity Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_physical_range_damage': 0.223,
            '%_critical_hit_damage': 0.25,
        },
    ),
    'Helical Ring': Item(
        name='Helical Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.25,
            '%_damage_against_burning': 0.13,
            '+_max_health': 31.0,
        },
    ),
    'Golden Spike Ring': Item(
        name='Golden Spike Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.08,
            '+_thorns_damage': 20.0,
        },
    ),
    # Not modeled: ReducedImpactOfSlowedBySlime, ChanceOnHitToApplySlipperyMovement
    'Crydra\'s Ring': Item(
        name='Crydra\'s Ring',
        item_category='Ring',
        set='HydraJewelrySet',
        consider_for='Both',
        attributes={
            '%_critical_hit_damage': 0.15,
        },
    ),
    'Lava Spike Ring': Item(
        name='Lava Spike Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_physical_melee_damage': 0.199,
            '%_critical_hit_damage': 0.24,
        },
    ),
    'Mold Ring': Item(
        name='Mold Ring',
        item_category='Ring',
        set='MoldRingAndNecklace',
        consider_for='Both',
        attributes={
            '%_critical_hit_chance': 0.16,
        },
    ),
    'Moonbell Ring': Item(
        name='Moonbell Ring',
        item_category='Ring',
        set='MoonbellSet',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.043,
            '%_magic_damage': 0.174,
        },
    ),
    'Nomad Ring': Item(
        name='Nomad Ring',
        item_category='Ring',
        set='NomadSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.246,
            '+_max_health': 66.0,
        },
    ),
    'Octarine Ring': Item(
        name='Octarine Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.094,
        },
    ),
    'Omoroth\'s Ring': Item(
        name='Omoroth\'s Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_damage_against_bosses': 0.2,
        },
    ),
    'Polished Octarine Ring': Item(
        name='Polished Octarine Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_melee_and_range_attack_speed': 0.091,
        },
    ),
    'Polished Swift Ring': Item(
        name='Polished Swift Ring',
        item_category='Ring',
        consider_for='Melee',
        attributes={
            '%_melee_attack_speed': 0.05,
        },
    ),
    'Scaled Ring': Item(
        name='Scaled Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_range_attack_speed': 0.051,
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Sky Ring': Item(
        name='Sky Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_physical_melee_damage': 0.233,
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Spine Ring': Item(
        name='Spine Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_damage_against_bosses': 0.43,
        },
    ),
    # Not modeled: ApplyPetDamageIncrease
    'Wildwarden Ring': Item(
        name='Wildwarden Ring',
        item_category='Ring',
        set='TamerSet',
        consider_for='Both',
        attributes={
            '%_damage': 0.158,
        },
    ),
    'Toothed Ring': Item(
        name='Toothed Ring',
        item_category='Ring',
        consider_for='Both',
        attributes={
            '%_melee_attack_speed': 0.048,
            '%_critical_hit_chance': 0.08,
        },
    ),
    'Samhain Curse Ring': Item(
        name='Samhain Curse Ring',
        item_category='Ring',
        set='SamhainSet',
        consider_for='Both',
        attributes={
            '%_damage': -0.088,
            '%_chance_to_apply_poison': 0.12,
        },
    ),
    'Flame Ring': Item(
        name='Flame Ring',
        item_category='Ring',
        set='FlameSet',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 37.0,
        },
    ),
    'Azure Ring': Item(
        name='Azure Ring',
        item_category='Ring',
        set='AzureSet',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.419,
        },
    ),
    'Boundary Ring': Item(
        name='Boundary Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '+_magic_barrier': 85.0,
        },
    ),
    'Brimstone Shard Ring': Item(
        name='Brimstone Shard Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '%_explosives_damage': 0.2,
            '+_magic_barrier': 42.0,
        },
    ),
    'Crescent Ring': Item(
        name='Crescent Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '+_max_mana': 58.0,
        },
    ),
    # Not modeled: ExplosionReduceManaCostByPercentage
    'Aether Ring': Item(
        name='Aether Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 2.9,
            '+_max_health': 29.0,
        },
    ),
    'Glow Tulip Ring': Item(
        name='Glow Tulip Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 3.7,
        },
    ),
    'Polished Glow Tulip Ring': Item(
        name='Polished Glow Tulip Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.116,
            '+_mana_regen': 2.3,
        },
    ),
    'Power Ring': Item(
        name='Power Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 3.1,
        },
    ),
    'Sacred Ring': Item(
        name='Sacred Ring',
        item_category='Ring',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 6.3,
        },
    ),
    'Warped Ring': Item(
        name='Warped Ring',
        item_category='Ring',
        set='WarpedSet',
        consider_for='Magic',
        attributes={
            '+_magic_barrier': 85.0,
        },
    ),
    'Hourglass Ring': Item(
        name='Hourglass Ring',
        item_category='Ring',
        consider_for='Summoning',
        attributes={
            '%_mana_reservation_reduction': 0.4,
        },
    ),
    'Jailor\'s Ring': Item(
        name='Jailor\'s Ring',
        item_category='Ring',
        consider_for='Summoning',
        attributes={
            '+_max_minions': 1.0,
            '%_mana_reservation_reduction': 0.21,
        },
    ),
    'Puppet Ring': Item(
        name='Puppet Ring',
        item_category='Ring',
        consider_for='Summoning',
        attributes={
            '%_minion_attack_speed': 0.48,
            '+_max_minions': 1.0,
        },
    ),
    # Not modeled: ExplosionReduceManaCostByPercentage
    'Vicious Ring': Item(
        name='Vicious Ring',
        item_category='Ring',
        consider_for='Summoning',
        attributes={
            '%_minion_damage': 0.289,
        },
    ),
}

BAGS = {
    'Morpha\'s Bubble Backpack': Item(
        name='Morpha\'s Bubble Backpack',
        item_category='Bag',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.2,
        },
    ),
    'Octarine Backpack': Item(
        name='Octarine Backpack',
        item_category='Bag',
        consider_for='Magic',
        attributes={
            '+_magic_barrier': 37.0,
        },
    ),
    'Scholar Backpack': Item(
        name='Scholar Backpack',
        item_category='Bag',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.189,
            '+_max_mana': 31.0,
        },
    ),
}

LANTERNS = {
    'Orb Lantern': Item(
        name='Orb Lantern',
        item_category='Lantern',
        consider_for='Melee',
        attributes={
            '%_mining_damage': 0.2,
        },
    ),
    'Pearl Lantern': Item(
        name='Pearl Lantern',
        item_category='Lantern',
        consider_for='Magic',
        attributes={
            '+_mana_regen': 2.6,
        },
    ),
    'Soul Lantern': Item(
        name='Soul Lantern',
        item_category='Lantern',
        consider_for='Summoning',
        attributes={
            '%_minion_attack_speed': 0.535,
        },
    ),
}

OFFHANDS = {
    'Omoroth\'s Beak': Item(
        name='Omoroth\'s Beak',
        item_category='Offhand',
        consider_for='Melee',
        attributes={
            '%_physical_melee_damage': 0.404,
        },
    ),
    # Not modeled: VisibleOreDistanceIncrease, ChanceForAdditionalOre
    'Core Iris': Item(
        name='Core Iris',
        item_category='Offhand',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 92.0,
        },
    ),
    'Octarine Shield': Item(
        name='Octarine Shield',
        item_category='Offhand',
        consider_for='Melee',
        attributes={
            '%_melee_and_range_attack_speed': 0.049,
            '+_max_health': 31.0,
        },
        has_durability=True,
    ),
    'Concealed Blade': Item(
        name='Concealed Blade',
        item_category='Offhand',
        consider_for='Melee',
        attributes={
            '%_critical_hit_chance': 0.12,
        },
    ),
    # Not modeled: ArmorPercentageIncrease
    'Crystal Meteor Chunk': Item(
        name='Crystal Meteor Chunk',
        item_category='Offhand',
        consider_for='Melee',
        attributes={
            '%_damage': 0.3,
        },
    ),
    'Hydra Tooth': Item(
        name='Hydra Tooth',
        item_category='Offhand',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.302,
            '%_triple_hit_chance': 0.05,
        },
    ),
    'Hookshot': Item(
        name='Hookshot',
        item_category='Offhand',
        consider_for='Melee',
        attributes={
            '+_mining_damage': 82.0,
        },
    ),
    'Smithing Glove': Item(
        name='Smithing Glove',
        item_category='Offhand',
        consider_for='Both',
        attributes={
            '%_damage_against_burning': 0.24,
        },
    ),
    'Gilded Hookshot': Item(
        name='Gilded Hookshot',
        item_category='Offhand',
        consider_for='Both',
        attributes={
            '%_melee_damage': 0.104,
            '%_range_damage': 0.088,
        },
    ),
    'Blue Leather Tome': Item(
        name='Blue Leather Tome',
        item_category='Offhand',
        set='SkullRingAndNecklace',
        consider_for='Both',
        attributes={
            '%_magic_damage': 0.198,
            '+_mana_regen': 3.4,
        },
    ),
    'Moonstone': Item(
        name='Moonstone',
        item_category='Offhand',
        consider_for='Magic',
        attributes={
            '+_max_mana': 31.0,
        },
    ),
    'Rift Lens': Item(
        name='Rift Lens',
        item_category='Offhand',
        consider_for='Magic',
        attributes={
            '%_magic_damage': 0.183,
        },
    ),
    'Minion Detonator': Item(
        name='Minion Detonator',
        item_category='Offhand',
        consider_for='Summoning',
        attributes={
            '%_minion_damage': 0.441,
        },
    ),
    'Scratched Stone': Item(
        name='Scratched Stone',
        item_category='Offhand',
        consider_for='Summoning',
        attributes={
            '%_minion_damage': 0.186,
            '+_max_minions': 1.0,
        },
    ),
}

PETS = {
    'Pheromoth': Item(
        name='Pheromoth',
        item_category='Pet',
        consider_for='Range',
        attributes={
            '%_physical_range_damage': 0.093,
            '%_triple_hit_chance': 0.1, # Configured by hand (stored in a chest, so its talents aren't in the save)
        }
    ),
    'Owlux': Item(
        name='Owlux',
        item_category='Pet',
        consider_for='Melee',
        attributes={
            '%_damage': 0.065,
            '%_triple_hit_chance': 0.08, # 4 Triple Trouble talents at 2% (as in your save)
        }
    ),
    # Buff pet; its talents (from your save) are what help melee and range. Magic: barrier and shorter mana regen delay
    # Buff pet: +1 minion and minion damage. Its talents (from your save) add more minion stats
    'Earie': Item(
        name='Earie',
        item_category='Pet',
        consider_for='Summoning',
        attributes={
            '%_minion_damage': 0.072,
            '+_max_minions': 1.0,
        },
    ),
    'Arcane Symbiote': Item(
        name='Arcane Symbiote',
        item_category='Pet',
        consider_for='Both',
        attributes={
            '+_magic_barrier': 19.0,
            '%_mana_regen_delay_reduction': 0.11,
        },
    ),
    # Attacks on its own (its damage isn't modeled); poisons targets
    'Fanhare': Item(
        name='Fanhare',
        item_category='Pet',
        consider_for='Both',
        attributes={
            '%_pet_poison_chance': 0.12,
        },
    ),
    # Attacks on its own (its damage isn't modeled); poisons targets
    'Jr. Purple Slime': Item(
        name='Jr. Purple Slime',
        item_category='Pet',
        consider_for='Both',
        attributes={
            '%_pet_poison_chance': 0.12,
        },
    ),
    # Attacks on its own (its damage isn't modeled); burns targets
    'Embertail': Item(
        name='Embertail',
        item_category='Pet',
        consider_for='Both',
        attributes={
            '+_burn_damage_on_hit': 20.0,
        },
    ),
}


def get_keys_for_damage_type(items_list, damage_type):
    """For each dictionary in items_list, the names of its items tried for damage_type"""
    from ck_dps_solver.model.item_stats import considered_for
    return [[k for k, v in items.items() if considered_for(v, damage_type)] for items in items_list]