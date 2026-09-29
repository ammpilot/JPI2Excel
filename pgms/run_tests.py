#!/usr/bin/env python3
"""Revision: 1. Run the regression suite without writing into upstream."""
import argparse
import sys
import unittest
sys.dont_write_bytecode = True
from _bootstrap import bootstrap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pattern', default='test_*.py', help='Test filename glob')
    parser.add_argument('--verbose', action='store_true', help='List individual tests')
    args = parser.parse_args()
    root = bootstrap()
    suite = unittest.defaultTestLoader.discover(str(root / 'tests'), pattern=args.pattern)
    result = unittest.TextTestRunner(verbosity=2 if args.verbose else 1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
