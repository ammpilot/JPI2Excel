# Third-party dependencies

Revision: 1

- **JPI-Parser / jpi-analyzer 0.2.0**, unicornlines, MIT license.
  Source: https://github.com/unicornlines/JPI-Parser
  Pinned commit: `e1a34c37d3cc2194699faba92e6666300cb85e86`.
  License: https://github.com/unicornlines/JPI-Parser/blob/e1a34c37d3cc2194699faba92e6666300cb85e86/LICENSE
  Used for binary delta unpacking, header parsing, and metric definitions.
  The project imports the dependency; no upstream source files are vendored.
- **openpyxl 3.1.5**, MIT license. Used for XLSX generation and test verification.
  Source: https://openpyxl.readthedocs.io/

Project-owned compatibility behavior and its regression evidence are documented
in `JPI-Format.md`. The sibling JPI-Parser repository is used read-only.
