"""Command line: ck-dps-solver (or python -m ck_dps_solver).

  ck-dps-solver                         open the window
  ck-dps-solver search [options]        run a search in the terminal and write the best loadouts to a CSV
  ck-dps-solver defaults                print every option as JSON (save it, edit it, pass it to search --config)
  ck-dps-solver --version

A config file holds only the options you change; nested ones (settings, skill_levels, perk_trees, save_filter,
consumables, fixed_items) are merged key by key into the defaults (defaults.py).
"""
import argparse
import copy
import json
import multiprocessing
import os
import sys

from ck_dps_solver import __version__, paths

DAMAGE_TYPES = ['Melee', 'Range', 'Magic', 'Summoning', 'Explosives']
MERGED_KEYS = ('settings', 'skill_levels', 'perk_trees', 'save_filter', 'consumables', 'fixed_items', 'best_fixed')


def merge_config(base, changes):
    """The defaults with a config file's changes (nested options merged key by key)"""
    config = copy.deepcopy(base)
    for key, value in changes.items():
        if key not in config:
            raise SystemExit(f'Unknown option in the config file: {key!r} (ck-dps-solver defaults lists them)')
        if key in MERGED_KEYS and isinstance(value, dict) and isinstance(config[key], dict):
            config[key] = dict(config[key], **value)
        else:
            config[key] = value
    return config


def build_config(args):
    from ck_dps_solver.defaults import default_config
    changes = {}
    if args.config:
        with open(args.config, encoding='utf8') as file:
            changes = json.load(file)
    # The default talents are the damage type's (defaults.perk_trees_for); the config file's talents still win
    config = merge_config(default_config(args.damage_type or changes.get('damage_type')), changes)
    if args.damage_type:
        config['damage_type'] = args.damage_type
    if 'perk_trees' not in changes: # The default talents also follow the mana strategy
        from ck_dps_solver.defaults import perk_trees_for
        config['perk_trees'] = perk_trees_for(config['damage_type'], config['settings'].get('Burst at full mana', True))
    if args.top is not None:
        config['top_n'] = args.top
    if args.character or args.world:
        config['save_filter'] = dict(config['save_filter'], enabled=True, player_files=args.character or [],
                                     world_files=args.world or [])
    if args.output:
        config['output'] = os.path.abspath(args.output)
    elif not os.path.isabs(config['output']):
        config['output'] = paths.user_file(config['output']) # Relative outputs go in the user folder
    return config


def run_search(args):
    from ck_dps_solver.engine.solver import run_search as search
    config = build_config(args)
    results, info = search(config, log=print if args.verbose else (lambda message: None))
    if results.empty:
        print('No loadouts found (no weapon of this damage type among the items searched?)')
    else:
        print(results.head(args.show).to_string(index=False))
    print(f"\n{info['loadouts']:,} loadouts in {info['seconds']:.1f}s. Best {len(results):,} written to {info['output']}")
    return 0


def print_defaults(args):
    from ck_dps_solver.defaults import default_config
    print(json.dumps(default_config(), indent=1))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='ck-dps-solver', description='Core Keeper DPS Solver: the best gear loadouts for your character. '
                                'Without a command, opens the window.')
    p.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    p.add_argument('--self-test', action='store_true', help=argparse.SUPPRESS) # Build check (app/main.py self_test)
    commands = p.add_subparsers(dest='command', metavar='command')
    commands.add_parser('gui', help='open the window (the default)')
    search = commands.add_parser('search', help='run a search in the terminal', description='Run a search and write the best loadouts to a CSV.')
    search.add_argument('--config', metavar='FILE', help='JSON file of the options to change (see: ck-dps-solver defaults)')
    search.add_argument('--damage-type', choices=DAMAGE_TYPES, help='overrides the config')
    search.add_argument('--character', metavar='SAVE', action='append',
                        help="search only items you own: a character save (saves/<n>.json in the game's save folder); repeatable")
    search.add_argument('--world', metavar='WORLD', action='append', help='a world save (worlds/<n>.world.gzip) for the items in its chests; repeatable')
    search.add_argument('--top', type=int, metavar='N', help='loadouts to keep in the CSV')
    search.add_argument('--output', metavar='CSV', help='where to write the loadouts (default: the outputs folder in your user folder)')
    search.add_argument('--show', type=int, default=10, metavar='N', help='loadouts to print (default 10)')
    search.add_argument('-v', '--verbose', action='store_true', help='print progress messages')
    search.set_defaults(handler=run_search)
    defaults = commands.add_parser('defaults', help='print every option as JSON')
    defaults.set_defaults(handler=print_defaults)
    return p


def main(argv=None):
    multiprocessing.freeze_support() # The packaged exe must not reopen the window in each search worker
    args = parser().parse_args(sys.argv[1:] if argv is None else argv)
    if args.command in (None, 'gui') or args.self_test:
        from ck_dps_solver.app.main import main as window
        return window(self_test=args.self_test)
    return args.handler(args)


if __name__ == '__main__':
    sys.exit(main())
