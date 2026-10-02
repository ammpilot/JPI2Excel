# JPI Legacy Trailing-Data Analysis — Conclusions

Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
All rights reserved.

Revision: 1

**Project:** JPI2Excel  
**Date:** 2026-09-28

## Bottom line

The bytes previously described as unexplained trailing data are best understood as **unused bytes in the final 256-byte binary block**.

The `$D` entries describe the logical allocations of the flight data.

The `$L` record describes the physical binary area in 256-byte blocks.

For all three supplied legacy files:

```text
$L = ceil((2 * sum($D halfsizes)) / 256)
```

and:

```text
$E_offset = data_start + ($L * 256)
```

exactly.

Therefore:

```text
logical_end  = data_start + 2 * sum($D halfsizes)
physical_end = data_start + $L*256
slack        = physical_end - logical_end
```

The slack is:

```text
U260731.JPI: 200 bytes
U260828.JPI: 196 bytes
U260919.JPI: 224 bytes
```

## What the slack is

The slack is not zero-filled.

Much of it happens to parse as complete, checksum-valid legacy JPI records.

The observed layout is:

```text
short fragment
complete checksum-valid records
partial record cut off at the 256-byte block boundary
```

That pattern is strongly consistent with **stale contents left in a reused instrument/download buffer or storage block** after new data overwrote only the beginning of the block.

Confidence:

```text
$L means 256-byte binary-block count for this legacy family: >99%
bytes after the $D allocations are final-block slack:        ~99%
record-shaped slack is stale prior block contents:           ~95%
identity/source flight of stale records:                     unknown
```

## What it is not

The slack should not be treated as:

- additional samples from the last declared flight;
- an extra undeclared flight;
- current data merely because individual records pass checksums;
- corruption merely because the bytes are nonzero;
- zero padding.

## Why valid checksums do not make it current-flight data

JPI flight records are delta/state based.

A record's absolute sensor values depend on the accumulated state from preceding records.

The surviving slack runs begin only after a fragment, so their original predecessor state is missing.

Even a perfectly checksum-valid orphan record cannot safely be assigned current-flight sensor values or timestamps.

## Required JPI2Excel change

The current strict check:

```text
$E must begin at the end implied by sum($D)
```

is wrong for these files.

Use the legacy framing:

```text
logical_end  = data_start + 2 * sum($D halfsizes)
physical_end = data_start + $L*256

require($L == ceil((logical_end - data_start) / 256))
require($E_offset == physical_end)
```

Decode flights only through `logical_end`.

Ignore `[logical_end, physical_end)` for flight decoding.

Optionally preserve/inspect those bytes in diagnostic mode.

## Regression requirements

All three original fixtures should parse successfully without being altered or truncated.

Accepting block slack must not change the decoded sample count or sensor values of any declared flight.

The original files should no longer fail with `EILSEQ` merely because `$E` is not at `logical_end`.
