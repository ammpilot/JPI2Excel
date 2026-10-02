# JPI Legacy Trailing-Data Analysis — Detailed Evidence

Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
All rights reserved.

Revision: 1

**Project:** JPI2Excel  
**Date:** 2026-09-28

## 1. Inputs

Analyzed original files:

```text
U260731.JPI
U260828.JPI
U260919.JPI
```

Also used:

```text
ExtraTrailingData.md Revision 1
```

The files were treated read-only.

The earlier diagnostic work had established that:

- all three contain bytes after the end calculated from `$D`;
- `$E,4*5D\r\n` ends each file;
- the larger trailing regions are separate from occasional single-byte per-flight word padding;
- long consecutive runs within those regions pass legacy framing and additive checksums.

The new investigation focused on whether another header field explains the exact physical boundary.

## 2. Relevant headers

### U260731.JPI

```text
$U,N2FR___*4E
$A,305,240,500,400,200,1700,220, 95*68
$F,0, 40, 35,8300,8300*58
$T, 7,31,26,16,24, 4396*6C
$C, 700,63741,32689, 1556, 306*4B
$D,  372,23254*40
$D,  373,16198*44
$L,309*5A
```

### U260828.JPI

```text
$U,N2FR___*4E
$A,305,240,500,400,200,1700,220, 95*68
$F,0, 40, 35,8300,8300*58
$T, 8,28,26,18,18, 4533*63
$C, 700,63741,32689, 1556, 306*4B
$D,  393, 9021*57
$D,  394, 9373*54
$D,  395, 6738*51
$D,  396, 5056*5E
$D,  397, 8811*59
$D,  398, 8209*55
$D,  399,10392*4E
$D,  400, 7070*50
$L,506*53
```

### U260919.JPI

```text
$U,N2FR___*4E
$A,305,240,500,400,200,1700,220, 95*68
$F,0, 40, 35,8300,8300*58
$T, 9,19,26,20,48, 4795*60
$C, 700,63741,32689, 1556, 306*4B
$D,  415, 5509*5D
$D,  416, 7332*52
$D,  417,  210*45
$D,  418,34069*41
$L,369*5C
```

## 3. Exact boundary arithmetic

A `$D` size is in 16-bit words:

```text
D_bytes = 2 * halfsize
```

Define:

```text
logical_binary_length = 2 * sum($D halfsizes)
logical_end = data_start + logical_binary_length
```

The key new observation is:

```text
physical_binary_length = $L * 256
physical_end = data_start + physical_binary_length
```

### U260731.JPI

```text
data_start = 194

sum($D halfsizes)
    = 23254 + 16198
    = 39452 words

logical_binary_length
    = 39452 * 2
    = 78904 bytes

logical_end
    = 194 + 78904
    = 79098

$L = 309

$L * 256
    = 309 * 256
    = 79104 bytes

physical_end
    = 194 + 79104
    = 79298

actual $E offset = 79298

slack
    = 79298 - 79098
    = 200 bytes

ceil(78904 / 256)
    = 309
    = $L
```

### U260828.JPI

```text
data_start = 308

sum($D halfsizes)
    = 9021 + 9373 + 6738 + 5056
      + 8811 + 8209 + 10392 + 7070
    = 64670 words

logical_binary_length
    = 64670 * 2
    = 129340 bytes

logical_end
    = 308 + 129340
    = 129648

$L = 506

$L * 256
    = 129536 bytes

physical_end
    = 308 + 129536
    = 129844

actual $E offset = 129844

slack
    = 129844 - 129648
    = 196 bytes

ceil(129340 / 256)
    = 506
    = $L
```

### U260919.JPI

```text
data_start = 232

sum($D halfsizes)
    = 5509 + 7332 + 210 + 34069
    = 47120 words

logical_binary_length
    = 47120 * 2
    = 94240 bytes

logical_end
    = 232 + 94240
    = 94472

$L = 369

$L * 256
    = 94464 bytes

physical_end
    = 232 + 94464
    = 94696

actual $E offset = 94696

slack
    = 94696 - 94472
    = 224 bytes

ceil(94240 / 256)
    = 369
    = $L
```

## 4. Combined evidence table

| Fixture | File size | `data_start` | `$D` logical bytes | Logical end | `$L` | `$L*256` | `$E` offset | Slack |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `U260731.JPI` | 79,307 | 194 | 78,904 | 79,098 | 309 | 79,104 | 79,298 | 200 |
| `U260828.JPI` | 129,853 | 308 | 129,340 | 129,648 | 506 | 129,536 | 129,844 | 196 |
| `U260919.JPI` | 94,705 | 232 | 94,240 | 94,472 | 369 | 94,464 | 94,696 | 224 |

All three satisfy exactly:

```text
$E_offset - data_start = $L * 256
$L = ceil(logical_binary_length / 256)
```

There is no rounding discrepancy in any fixture.

## 5. Final-block occupancy

The logical data consume only the beginning of the final 256-byte physical block.

For each file:

```text
bytes_in_last_declared_block =
    logical_binary_length - (($L - 1) * 256)
```

Results:

```text
U260731: 56 bytes declared, 200 bytes slack
U260828: 60 bytes declared, 196 bytes slack
U260919: 32 bytes declared, 224 bytes slack
```

The first two files each have one byte of word-alignment padding after the last complete declared record.

Thus the final physical blocks are approximately:

```text
U260731:
    55 bytes valid current record data
     1 byte declared word pad
   200 bytes block slack

U260828:
    59 bytes valid current record data
     1 byte declared word pad
   196 bytes block slack

U260919:
    32 bytes valid current record data
     0 bytes declared word pad
   224 bytes block slack
```

## 6. Structure inside the slack

Earlier diagnostic scanning found:

| Fixture | Prefix before valid run | Valid records | Run bytes | Suffix after valid run |
|---|---:|---:|---:|---:|
| `U260731.JPI` | 3 | 16 | 196 | 1 |
| `U260828.JPI` | 4 | 10 | 184 | 8 |
| `U260919.JPI` | 12 | 16 | 206 | 6 |

Absolute valid-run ranges:

```text
U260731: [79101, 79297)
U260828: [129652, 129836)
U260919: [94484, 94690)
```

Unexplained prefixes:

```text
U260731: 02 05 c6
U260828: 02 01 1e cc
U260919: 10 0b 1b 10 12 1e 07 08 05 0e b3 02
```

Trailing fragments:

```text
U260731: 06

U260828:
25 25 00 2a 80 03 02 00

U260919:
21 21 00 03 02 00
```

The August and September trailing fragments begin with matching duplicate masks, as a legacy record would.

## 7. Interpretation

### 7.1 Strong conclusion: physical block slack

The exact `$L` relationship explains why bytes exist after the sum of the `$D` allocations.

The binary transfer/storage area is physically rounded to a 256-byte boundary.

Therefore the region is not "mystery extra flight data" in the structural sense. It is the unused part of the final physical block.

### 7.2 Strong inference: stale previous block contents

If the unused portion of a previously populated 256-byte buffer/page is not cleared before the current write, the expected pattern is:

```text
old record stream:
[record][record][record][record]...

new data overwrites the block prefix:
[NEW NEW NEW NEW NEW][tail of old record][old record][old record]...[partial old]
                    ^ write stops                       ^ 256-byte boundary
```

That predicts:

1. a short fragment immediately after current data because the beginning of an old record was overwritten;
2. complete old records beginning at the next pre-existing record boundary;
3. valid checksums on those complete surviving records;
4. a final partial record where the 256-byte block ends.

That is exactly the observed qualitative pattern in all three fixtures.

### 7.3 Why they are unlikely to be additional current-flight data

Several independent points argue against appending them:

- `$D` already supplies an explicit logical length.
- `$L` independently explains the physical end exactly.
- the first slack bytes do not continue as a valid record stream from the declared current flight;
- decoding only becomes record-valid after skipping a fragment;
- the valid sequence is truncated exactly at the physical block boundary;
- stateful delta records cannot be safely reattached after skipped bytes;
- there is no independent flight header or timestamp for the surviving sequence.

The record-shaped bytes are therefore not safe recoverable samples.

## 8. Search for exact duplication

No exact copy of the complete checksum-valid slack run was established earlier within the same file or among the other two current fixtures.

That does not weaken the stale-buffer interpretation materially: stale contents could come from a prior flight/download not present in the current file, and delta records vary substantially even when engine conditions are similar.

It does mean that the exact origin of the stale bytes has not been identified.

## 9. Confidence

Suggested confidence levels:

```text
$L is a 256-byte physical binary-block count for these legacy files:
    >99.5%

bytes after the sum of $D allocations and before $E are final-block slack:
    ~99%

record-shaped slack is stale prior contents of a reused buffer/page:
    ~95%

specific earlier flight/download that produced those bytes:
    not determinable from current evidence
```

## 10. Safe implementation rule

For the validated legacy family:

```python
logical_len = 2 * sum(d.halfsize for d in directory)
logical_end = data_start + logical_len

physical_len = L_value * 256
physical_end = data_start + physical_len

expected_L = (logical_len + 255) // 256

if L_value != expected_L:
    # unexpected legacy framing
    error_or_diagnostic()

if E_offset != physical_end:
    # unexpected legacy framing
    error_or_diagnostic()

decode_flights_only_within_D_allocations()
ignore_for_flight_data(file_bytes[logical_end:physical_end])
```

Do not resynchronize inside slack for normal decoding.

## 11. Suggested diagnostic metadata

The parser may expose:

```text
logical_binary_length
physical_binary_length
block_size = 256
block_count = $L
block_slack_length
block_slack_nonzero
block_slack_contains_record_like_data   # diagnostic only
```

Do not expose the stale records as flight samples.

## 12. Required regression tests

For each original fixture:

1. parse the unmodified original file;
2. verify the exact `$L` relationship;
3. verify `$E` at `data_start + $L*256`;
4. verify the expected slack length;
5. decode only `$D`-declared flights;
6. ensure sample counts and values are unchanged versus declared-block decoding;
7. ensure strict mode does not return `EILSEQ` solely because slack is nonzero;
8. optionally verify known slack structure diagnostically.

No test should need to construct a truncated replacement fixture merely to satisfy boundary validation.

## 13. Remaining unknowns

Still unknown:

- whether the block is a flash-memory page, RAM buffer, serial-transfer block, or other internal object;
- whether every legacy EDM-700/800 software revision uses the same `$L` semantics;
- whether some legacy files intentionally clear the slack;
- the source flight/session of the surviving record bytes.

Those are implementation-independent questions.

For JPI2Excel's current files, the framing rule is sufficiently well supported to stop treating the original files as malformed.
