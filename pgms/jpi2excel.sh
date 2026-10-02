#!/usr/bin/env bash
# Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
# All rights reserved.

# Revision: 2. Bash launcher; pass --help for usage.
set -e

jpi_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$jpi_script_dir/jpi2excel.py" "$@"
