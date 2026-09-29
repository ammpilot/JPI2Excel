# Extra trailing data in the legacy JPI fixtures

**Revision:** 2  
**Revision date:** 2026-09-29  
**Project:** JPI2Excel

## Resolution (2026-09-29)

The original investigation below is retained as historical evidence. Its unresolved
framing interpretation and reported rejection behavior are superseded by
[JPI-Format.md Revision 4](JPI-Format.md) and the
[trailing-data conclusions](JPI-Trailing-Data-Summary.md).

`$L` gives the physical binary length in 256-byte blocks, while `$D` entries give
the logical flight allocations. The extra bytes are unused final-block space.
JPI2Excel now validates the `$L` relationship and `$E` at the physical end, accepts
all three original files, and excludes this slack from flight decoding. Sensor
values, timestamps, and sample counts remain unchanged. Its origin as stale buffer
contents remains an inference. Original source files are unchanged.

## Historical summary

All three original fixtures contain binary bytes between the nominal end of the
last flight, calculated from the `$D` directory entries, and the `$E` end marker.
Closer inspection found consecutive runs of checksum-valid, flight-like records
inside these regions. Calling the entire region garbage or corrupt data would
overstate the evidence.

At Revision 1, the implementation rejected the unexplained remainder under its
strict validation policy. That rejection reflected an unresolved format rule; it did
not establish that the original downloads are damaged.

This document supplements the initial trailing-byte observations in
`JPI-Format.md` Revision 3 and `JPI-Project-Notes.md` Revision 3.

## Files and nominal boundaries

A `$D` entry supplies a flight number and a nominal size in 16-bit words. The
nominal end of the binary flight area is calculated as:

```text
nominal_end = first_binary_byte_offset + sum(each_directory_size * 2)
extra_length = end_marker_offset - nominal_end
```

All offsets below are decimal, zero-based byte offsets. End offsets are exclusive:
`nominal_end` points to the first unexplained byte, and `end_marker_offset` points
to the `$` of `$E`.

| Fixture | File size | First binary byte | Last flight | Nominal end | `$E` offset | Extra bytes |
|---|---:|---:|---:|---:|---:|---:|
| `U260731.JPI` | 79,307 | 194 | 373 | 79,098 | 79,298 | 200 |
| `U260828.JPI` | 129,853 | 308 | 400 | 129,648 | 129,844 | 196 |
| `U260919.JPI` | 94,705 | 232 | 418 | 94,472 | 94,696 | 224 |

All three files end immediately after this nine-byte ASCII record:

```text
$E,4*5D\r\n
```

Its XOR checksum is valid. These files have no bytes after that marker, no `$V`
trailer, and no trailing configuration XML.

The binary flight headers and complete records consumed inside the nominal
flight blocks pass their additive checksums. Some nominal blocks also contain
a single leftover byte, currently treated as word-alignment padding. The larger
extra regions described here are separate from those individual leftover bytes.

## Closer inspection of the extra regions

Attempting to continue decoding directly from the end of the last successfully
decoded record encounters unequal record masks or a checksum failure. However,
searching candidate byte offsets within the extra region reveals long consecutive
runs with valid legacy record structure and additive checksums.

| Fixture | Leading bytes before valid run | Valid records in run | Run length in bytes | Bytes after run, before `$E` |
|---|---:|---:|---:|---:|
| `U260731.JPI` | 3 | 16 | 196 | 1 |
| `U260828.JPI` | 4 | 10 | 184 | 8 |
| `U260919.JPI` | 12 | 16 | 206 | 6 |

Each row accounts for the entire extra region: leading bytes + run length +
remaining bytes = extra length.

The runs occupy these absolute half-open byte ranges:

| Fixture | Run start | Run end |
|---|---:|---:|
| `U260731.JPI` | 79,101 | 79,297 |
| `U260828.JPI` | 129,652 | 129,836 |
| `U260919.JPI` | 94,484 | 94,690 |

The final byte in July's file is `06`, insufficient to identify a complete
record. The final fragments in the other two files begin with matching masks
and resemble incomplete records:

```text
U260828.JPI: 25 25 00 2a 80 03 02 00
U260919.JPI: 21 21 00 03 02 00
```

The unexplained prefixes before the valid runs are:

```text
U260731.JPI: 02 05 c6
U260828.JPI: 02 01 1e cc
U260919.JPI: 10 0b 1b 10 12 1e 07 08 05 0e b3 02
```

These observations establish that much of the extra region has flight-record
structure. They do not establish which flight or download those records belong
to, or whether the preceding and following fragments are expected firmware output.

## Inspection method

The investigation used the original files read-only and compared their structure
with the local upstream JPI-Parser source and `filespec.md`, pinned at commit
`e1a34c37d3cc2194699faba92e6666300cb85e86`.

For candidate legacy records, the diagnostic scan checked:

1. The two leading mask bytes agree.
2. The repeat-count byte and mask-selected control bytes are present.
3. The required sign bytes are present. For the legacy eight-bit mask, indices
   0 through 5 carry sign bytes; indices 6 and 7 use the referenced signs.
4. The control bits determine a complete delta-byte payload and trailing checksum.
5. The sum of the entire record is zero modulo 256.
6. The next record starts immediately after the preceding checksum, allowing a
   consecutive run to be measured without additional skipped bytes.

The candidate scan stopped before `$E`; bytes from the ASCII marker were not
used to complete a binary record. This was a diagnostic framing/checksum scan,
not an approved recovery algorithm or an independent verification of sensor values.

## Interpretation and uncertainty

The extra regions are not ordinary zero padding or readable metadata. Plausible
explanations include:

- Additional final-flight data extending beyond the directory's nominal length.
- Stale contents from an instrument or download buffer.
- A legacy structure or termination convention that is not yet understood.

None of these explanations is established. Similar behavior in three downloads
from the same apparent legacy format makes a systematic format or firmware
convention worth investigating.

Checksum-valid records alone are insufficient for safe recovery. Sensor values
are reconstructed using accumulated deltas. Skipping unexplained bytes may omit
state changes, and the initial state for a newly found run has not been verified.
Appending these runs could therefore produce incorrect values or timestamps even
when every appended record passes its own checksum.

## Program behavior before the framing correction

The pinned upstream parser reads the nominal `$D` sizes and ignores the remainder
before `$E`. At Revision 1, JPI2Excel required `$E` at the nominal end and rejected these
three original files with `EILSEQ` because that boundary check fails.

Existing declared-block regression tests explicitly construct temporary in-memory
variants ending after the nominal blocks. Those tests characterize the declared
data and exercise exports; they do not prove that the nominal blocks contain all
valid final-flight data. The variants are not replacements for the source fixtures.

Neither the original fixtures nor the sibling JPI-Parser repository was modified
during this investigation. No parser policy was changed as a result of the closer
inspection.

## Original investigation recommendations

- Compare final-flight sample counts and ending values with JPI's own Windows
  software, if available. No such comparison has been performed yet.
- Investigate legacy download termination and buffer behavior using additional
  source material or fixtures.
- Determine whether the unexplained prefixes and final fragments have a defined
  role before treating them as padding, recoverable records, or corruption.
- Add regression evidence before changing validation or decoding. Any accepted
  treatment should explicitly account for these bytes rather than silently
  discarding or appending them.
