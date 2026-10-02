# Excel graphing

Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
All rights reserved.

Revision: 5 — 2026-09-30; implemented in JPI2Excel 2.0.0.

Use `--graph` or `--graphs` with `--xls` or `--xls-separate`. Each selected
Flight sheet is immediately followed by its Graph sheet, including duplicate-name
suffixes: `Flight 415 (2)`, then `Graph 415 (2)`. Separate workbooks include their
own graph sheet plus a hidden Summary sheet supplying conditional-formatting
limits. Without either option, no graphs are added. Both aliases are fatal with
`--csv`, including `--info --csv`.
They are ignored for non-export actions. With `--info --xls` or
`--info --xls-separate`, the requested graphs are included.

## Charts and source values

The visual reference is `data/CanonicalGraph.xlsx`, sheet `Graph 415`, including
its updated Delta T references. The program encodes its styling; the reference
workbook is not a runtime dependency and is not modified.

Each graph sheet has two native, editable Excel charts:

| Title | Primary (left) axis | Secondary (right) axis | Alarm line |
|---|---|---|---|
| Flight N Exhaust Temperatures | EGT and TIT channels | FF | TIT high alarm, labeled TIT Limit |
| Flight N Cylinder Temperatures | CHT channels and Oil T | RPM | CHT high alarm, labeled CHT Limit |

Every sensor series links to its Flight sheet's numeric Delta T column for X
values and to its corresponding data column for Y values. Straight-line XY
charts give elapsed seconds proportional spacing even when recording intervals
change. The horizontal axis is labeled `Time (seconds)`, from zero to the last
sample's Delta T, with readable numeric tick spacing and thousands separators
(for example, 500, 1,000, 1,500). Only the primary horizontal axis has a title
and tick labels; the secondary horizontal axis is hidden and has no title.
A zero-duration flight uses
a one-second axis span so Excel can display it.

Alarm lines use the same normalized source alarm values reported in Summary
and `--info`. They contain two equal Y values at the plot's horizontal endpoints,
so the lines span the plot. They are solid red, 2 pixels (19,050 EMU) wide.
Alarm values and axis bounds are calculated at export time; editing a Summary
cell later does not recalculate a chart's limit or bounds. Separate workbooks show graph limits while their Summary sheet is hidden.

Missing channels and channels with no numeric readings are omitted from charts;
individual missing readings remain gaps. An absent threshold produces no alarm
line. An absent FF/RPM series also omits its secondary axis. If a chart has no
temperature readings, it is omitted with a nonfatal warning on stderr and, when
present, in Summary. Its Graph sheet remains in the expected position.

## Axis bounds

Compute maxima from nonblank readings, add the indicated padding, then round
up to the specified multiple. Include a threshold only if it is present.

| Axis | Maximum before rounding | Round up to |
|---|---|---|
| Exhaust primary | max(TIT high alarm, all TIT and EGT readings) + 100 | 100 |
| Exhaust secondary | max(all FF readings) + 1 | 1 |
| Cylinder primary | max(CHT high alarm, all CHT and Oil T readings) + 25 | 50 |
| Cylinder secondary | max(all RPM readings) + 100 | 100 |

Both primary-axis minima and the RPM-axis minimum are the minimum of all values
plotted on that axis, rounded down to the next multiple of 100 (including plotted
alarm lines). The FF-axis minimum is 1, as requested, so readings below 1 are
outside its visible range. If the FF maximum formula yields 1 or less, use 2 to
keep the axis span valid. Negative readings are preserved in the source data.
Axis unit labels come from the source metadata, not assumed Fahrenheit/gallons.

## Appearance

Cylinder colors are consistent between EGT and CHT and remain attached to the
cylinder number when other channels are missing:

| Cylinder | Color (RGB) |
|---|---|
| 1 | FFC000 (gold) |
| 2 | 00B050 (green) |
| 3 | 00B0F0 (cyan) |
| 4 | 0070C0 (blue) |
| 5 | 7030A0 (purple) |
| 6 | 945200 (brown) |
| 7–12 | E97132, D86ECC, 008080, 808000, A64D79, 5C677D |

Further cylinders receive deterministic additional hues. TIT and Oil T are solid
navy (`002060`); FF and RPM use the same navy with the reference's `sysDash`
pattern. Sensor lines are 3 pixels wide, with round ends, no markers, and no
smoothing. Chart titles use Cambria 14; axis titles Cambria 10; tick labels and
bottom legends Calibri 9. Primary axes have light-gray horizontal gridlines.
Charts use the reference's two-cell anchors beginning at B2 and B52, each 48 rows
high. Fonts and pixel rendering can vary with the Excel/viewer environment.

## Summary simplification

Summary has three columns: Source (85 pixels), Property (225 pixels), and Value
(450 pixels, wrapping). The redundant Input ordinal is removed. The header row
and Source/Property columns remain frozen. Datetimes still display to seconds.

## Future multi-engine graphs (not implemented)

Keep one Graph sheet per flight, directly after the matching Flight sheet. It
will contain one two-chart set per engine, with per-engine data, alarms, and axis
bounds. Titles identify the engine, for example
`Flight 415 Exhaust Temperatures, Left Engine`. Use Left/Right for two engines;
Left/Center/Right for three; engine numbers for four or more. Preserve cylinder
color assignments in every set and use the shared flight Delta T timeline.

This requirement includes future formats unsupported by JPI-Parser. Version 2
does not add multi-engine decoding or change the current single-engine selection
policy. Real fixtures or authoritative format evidence remain prerequisites for
implementing those decoders.
