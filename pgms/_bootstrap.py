# Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
# All rights reserved.

"""Revision: 2. Read-only development access to the pinned sibling dependency."""
from pathlib import Path
import subprocess
import sys


def bootstrap():
    sys.dont_write_bytecode = True
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'src'))
    try:
        import jpi_analyzer
    except ImportError:
        sibling = root.parent / 'JPI-Parser'
        if sibling.is_dir():
            from jpi2excel import UPSTREAM_REVISION
            revision = subprocess.check_output(['git', '-C', str(sibling), 'rev-parse', 'HEAD'], text=True).strip()
            dirty = subprocess.run(['git', '-C', str(sibling), 'diff', '--quiet', 'HEAD', '--', 'jpi_analyzer'], check=False)
            if revision != UPSTREAM_REVISION or dirty.returncode:
                raise RuntimeError('Sibling JPI-Parser must match the clean pinned revision ' + UPSTREAM_REVISION)
            sys.path.insert(0, str(sibling))
    return root
