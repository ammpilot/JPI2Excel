#!/usr/bin/env python3
"""Revision: 1. Development CLI; --help lists all options."""
import sys
sys.dont_write_bytecode = True
from _bootstrap import bootstrap
bootstrap()
from jpi2excel.cli import main
raise SystemExit(main())
