# AGENTS.md

Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
All rights reserved.

Revision: 1

## Project

This repository is for a macOS-friendly JP Instruments `.JPI` engine-monitor data converter, initially targeting EDM-800 files and Excel `.xlsx` output.

## Working guidance

- Use Python for parsing, validation, transformation, and Excel generation.
- Keep shell scripting optional and thin.
- Prefer the MIT-licensed `unicornlines/JPI-Parser` project as the decoding layer rather than reimplementing the binary format.
- Read `docs/JPI-Project-Notes.md` when working on project architecture, setup, goals, or milestones.
- Read `docs/JPI-Format.md` when changing parser behavior, sensor mappings, time decoding, checksums, units, or test fixtures.
- Treat `.JPI` source data as authoritative; do not silently "fix" unusual metadata or values.
- Add or update regression tests before changing format-decoding behavior.
- Make unsupported/corrupt input fail visibly or produce an explicit warning; do not silently invent values.
- Keep third-party code and this project's code clearly separated.
- Preserve upstream MIT attribution if upstream source code is vendored or copied.
- Do not commit private credentials, local virtual environments, generated Excel output, or aircraft-identifying sample data unless explicitly intended.
- All created files (not those sourced from elsewhere) should have a revision number in them. A comment is fine.
- All user-executable programs should have a --help option that provide usage info.

## Initial technical direction

Use JPI-Parser through a pinned/reproducible dependency first. Build the project-specific Excel exporter around its decoded Python objects.

Use `openpyxl` for `.xlsx` output unless a concrete requirement justifies another library.

## Before substantial parser changes

Run the existing tests, inspect the relevant sample file behavior, and compare against upstream JPI-Parser. When possible, compare decoded output with JPI's own Windows software.

## Scope discipline

Keep `AGENTS.md` concise. Put durable technical detail in the project documentation rather than expanding this file with one-off task instructions.
