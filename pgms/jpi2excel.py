#!/usr/bin/env python3
# Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
# All rights reserved.

"""Revision: 2. Development CLI; --help lists all options."""
import sys
sys.dont_write_bytecode = True
from _bootstrap import bootstrap
bootstrap()
from jpi2excel.cli import main
raise SystemExit(main())
