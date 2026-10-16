# PyInstaller build of the Windows app. From the repository:
#   pip install .[build]
#   pyinstaller packaging/ck-dps-solver.spec
# The app is in dist/CK DPS Solver/ (run "CK DPS Solver.exe"; ship the whole folder). A folder build starts much faster
# than --onefile, which would unpack ~300 MB (numpy, pandas, numba/LLVM) on every launch. The release workflow
# (.github/workflows/release.yml) runs this and zips the folder.
import glob
import os
import re

from PyInstaller.utils.win32.versioninfo import (FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct,
                                                VSVersionInfo)

ROOT = os.path.dirname(SPECPATH) # noqa: F821 (SPECPATH: this file's folder, set by PyInstaller)
PACKAGE = os.path.join(ROOT, 'src', 'ck_dps_solver')

VERSION = re.search(r"__version__ = '([^']+)'", open(os.path.join(PACKAGE, '__init__.py'), encoding='utf8').read()).group(1)
NUMBERS = tuple(int(n) for n in re.findall(r'\d+', VERSION)[:3]) + (0,)
version_info = VSVersionInfo( # The exe's Properties > Details
    ffi=FixedFileInfo(filevers=NUMBERS, prodvers=NUMBERS),
    kids=[StringFileInfo([StringTable('040904B0', [
              StringStruct('ProductName', 'Core Keeper DPS Solver'), StringStruct('FileDescription', 'Core Keeper DPS Solver'),
              StringStruct('ProductVersion', VERSION), StringStruct('FileVersion', VERSION),
              StringStruct('LegalCopyright', 'MIT License, sinisterbot'), StringStruct('OriginalFilename', 'CK DPS Solver.exe')])]),
          VarFileInfo([VarStruct('Translation', [1033, 1200])])])

datas = [(os.path.join(PACKAGE, 'data'), 'ck_dps_solver/data')] # wiki_data.json, the icons
# numba caches compiled code only when it can find each module's Python source: ship the sources next to the bytecode
for path in glob.glob(os.path.join(PACKAGE, '**', '*.py'), recursive=True):
    datas.append((path, os.path.normpath(os.path.join('ck_dps_solver', os.path.relpath(os.path.dirname(path), PACKAGE)))))

a = Analysis( # noqa: F821
    [os.path.join(SPECPATH, 'launcher.py')], # noqa: F821
    pathex=[os.path.join(ROOT, 'src')],
    datas=datas,
    hiddenimports=['PySide6.QtCharts'],
    excludes=['tools', 'tests', 'matplotlib', 'IPython', 'pytest', 'tkinter'],
)
pyz = PYZ(a.pure) # noqa: F821
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='CK DPS Solver', console=False, # noqa: F821
          icon=os.path.join(SPECPATH, 'icon.ico'), version=version_info) # noqa: F821
coll = COLLECT(exe, a.binaries, a.datas, name='CK DPS Solver') # noqa: F821
