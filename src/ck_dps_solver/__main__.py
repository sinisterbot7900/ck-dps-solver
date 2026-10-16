"""python -m ck_dps_solver: the window, or the command line with arguments (python -m ck_dps_solver --help)"""
import sys

from ck_dps_solver.cli import main

if __name__ == '__main__':
    sys.exit(main())
