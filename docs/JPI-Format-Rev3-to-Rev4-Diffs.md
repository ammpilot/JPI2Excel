# JPI-Format Revision 3 → Revision 4 Changes

**Project:** JPI2Excel  
**Date:** 2026-09-28  
**Target file:** `JPI-Format.md`

## Important note

The exact Revision 3 `JPI-Format.md` file was not supplied with this handoff.

Therefore this document is a **semantic change specification**, not a line-for-line unified diff. It is based on:

- `ExtraTrailingData.md` Revision 1, which states what remained unresolved after Revision 3;
- direct inspection of `U260731.JPI`, `U260828.JPI`, and `U260919.JPI`;
- the new arithmetic relationship involving `$L`.

Codex should update the repository's actual Revision 3 file while preserving any unrelated Revision 3 content.

## Required metadata change

Change:

```text
Revision: 3
```

to:

```text
Revision: 4
Revision date: 2026-09-28
```

Add a revision-history entry equivalent to:

```text
Revision 4: Identified `$L` as a 256-byte binary-block count for all three
legacy fixtures; reclassified bytes after the logical `$D` data as final-block
slack rather than additional flight data; updated strict validation rules.
```

## Replace the unresolved trailing-data interpretation

Revision 3 / `ExtraTrailingData.md` treated the bytes between:

```text
logical_end = data_start + 2 * sum($D halfsizes)
```

and `$E` as unexplained.

Replace that unresolved framing with the following strongly supported legacy rule:

```text
logical_binary_length  = 2 * sum($D halfsizes)
logical_end            = data_start + logical_binary_length

physical_binary_length = $L_value * 256
physical_end           = data_start + physical_binary_length

expected_L             = ceil(logical_binary_length / 256)
```

For each current fixture:

```text
$L_value == expected_L
$E_offset == physical_end
```

The interval:

```text
[logical_end, physical_end)
```

is final physical-block slack and is not part of a declared flight.

## Add exact evidence table

Add:

| Fixture | `data_start` | `$D` bytes | `$L` | `$L*256` | `$E` offset | Slack |
|---|---:|---:|---:|---:|---:|---:|
| `U260731.JPI` | 194 | 78,904 | 309 | 79,104 | 79,298 | 200 |
| `U260828.JPI` | 308 | 129,340 | 506 | 129,536 | 129,844 | 196 |
| `U260919.JPI` | 232 | 94,240 | 369 | 94,464 | 94,696 | 224 |

State explicitly:

```text
$E_offset - data_start == $L * 256
$L == ceil($D_bytes / 256)
```

for all three fixtures.

## Reclassify the checksum-valid trailing records

Do not describe the entire region as corruption or additional current-flight data.

Document:

- the slack is nonzero, non-ASCII, and not zero-filled;
- long sequences inside it satisfy legacy record framing and additive checksums;
- the slack starts with a short non-record fragment and ends with a partial record;
- this pattern is strongly consistent with stale prior contents of a reused 256-byte buffer/page;
- stale-buffer interpretation is an inference, not an official JPI-documented fact;
- the exact source flight/session of those bytes is unknown.

Known diagnostic runs:

```text
U260731.JPI:
    slack prefix fragment = 3 bytes
    valid records = 16
    valid-run length = 196 bytes
    trailing fragment = 1 byte

U260828.JPI:
    slack prefix fragment = 4 bytes
    valid records = 10
    valid-run length = 184 bytes
    trailing fragment = 8 bytes

U260919.JPI:
    slack prefix fragment = 12 bytes
    valid records = 16
    valid-run length = 206 bytes
    trailing fragment = 6 bytes
```

## Distinguish two different forms of unused bytes

Preserve the distinction between:

1. optional one-byte padding inside a `$D` flight allocation because `$D` is measured in 16-bit words; and
2. final-block slack after the sum of all `$D` allocations and before `$E`.

The first belongs to a declared `$D` allocation.

The second does not belong to any declared flight.

## Change strict validation behavior

Remove/revise any rule equivalent to:

```text
require($E_offset == logical_end)
```

For the current legacy format, replace it with validation equivalent to:

```text
logical_binary_length = 2 * sum($D halfsizes)
logical_end = data_start + logical_binary_length

physical_binary_length = L_value * 256
physical_end = data_start + physical_binary_length

require(L_value == ceil(logical_binary_length / 256))
require($E_offset == physical_end)
require(logical_end <= physical_end)
require(0 <= physical_end - logical_end < 256)
```

Do not apply this blindly to unrelated later JPI formats; scope it to the legacy path for which the relationship is validated.

## Change flight decoding boundary

Flight decoding must end at:

```text
logical_end
```

not at `$E`.

Do not attempt to resynchronize within the block slack and append checksum-valid records to the final flight.

Reason: JPI records are delta/state based, and orphaned valid records cannot safely be assigned current-flight absolute values or timestamps.

## Change error policy

The three original fixtures must no longer fail with `EILSEQ` solely because `$E` is later than `logical_end`.

If:

```text
$L == ceil(logical_binary_length / 256)
```

and:

```text
$E_offset == data_start + $L*256
```

then nonzero slack is expected/acceptable for this legacy framing.

Unexpected relationships should still produce a diagnostic or error.

## Add/modify regression tests

Add tests for all three source fixtures with these exact values:

```text
U260731: data_start 194, D bytes 78904, L 309, E 79298, slack 200
U260828: data_start 308, D bytes 129340, L 506, E 129844, slack 196
U260919: data_start 232, D bytes 94240, L 369, E 94696, slack 224
```

Assert:

```text
L == ceil(D_bytes / 256)
E == data_start + L*256
```

and that exported flight sample counts do not change when the slack is accepted.

Tests may inspect record-shaped slack diagnostically, but no slack record may become a flight sample.

## Preserve uncertainty wording

Use strong wording for the observed block relationship:

> In all three current legacy fixtures, `$L` exactly describes the binary area's
> length in 256-byte blocks.

Use qualified wording for the stale-buffer explanation:

> The fragment / complete-record-run / fragment pattern is strongly consistent
> with stale contents of a reused block, but the exact firmware/storage mechanism
> has not been independently documented.

## No required change to declared-flight decoding

The existing upstream behavior of respecting `$D` lengths remains appropriate for the flight data itself.

The required code change is primarily in JPI2Excel's strict file-boundary validation and diagnostics.
