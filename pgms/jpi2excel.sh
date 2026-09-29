#!/usr/bin/env bash
# Revision: 1. Bash launcher; pass --help for usage.
set -e

jpi_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$jpi_script_dir/jpi2excel.py" "$@"
