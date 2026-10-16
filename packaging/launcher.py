"""Opens the app: the same as the ck-dps-solver command. Run it from a clone (python packaging/launcher.py) without
installing; the packaged exe (packaging/ck-dps-solver.spec) also starts here."""
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if os.path.isdir(SRC) and SRC not in sys.path: # From a clone: use the package in src/
    sys.path.insert(0, SRC)

from ck_dps_solver.cli import main  # noqa: E402

if __name__ == '__main__':
    sys.exit(main())
