# Third-party dependencies

Project-specific documentation:
Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
All rights reserved.

Revision: 3

The project notice above does not replace or restrict the upstream MIT notice
reproduced below.

- **JPI-Parser / jpi-analyzer 0.2.0**, unicornlines, MIT license.
  Source: https://github.com/unicornlines/JPI-Parser
  Pinned commit: `e1a34c37d3cc2194699faba92e6666300cb85e86`.
  License: https://github.com/unicornlines/JPI-Parser/blob/e1a34c37d3cc2194699faba92e6666300cb85e86/LICENSE
  Used for binary delta unpacking, header parsing, and metric definitions.
  `src/jpi2excel/reader.py` adapts decoder orchestration from
  `jpi_analyzer/decoder.py` and extends upstream classes with strict validation
  and legacy compatibility behavior. The adapted file repeats the complete
  upstream MIT license and identifies its pinned source revision.
  Other modules import the dependency; no complete upstream source files are vendored.
- **openpyxl 3.1.5**, MIT license. Used for XLSX generation and test verification.
  Source: https://openpyxl.readthedocs.io/

Project-owned compatibility behavior and its regression evidence are documented
in `JPI-Format.md`. The sibling JPI-Parser repository is used read-only.

## JPI-Parser MIT license

The following license applies to upstream-derived portions, including those
in `src/jpi2excel/reader.py`.

```text
MIT License

Copyright (c) 2026 Unicornlines

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
