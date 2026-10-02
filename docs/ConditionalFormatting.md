# Flight alarm conditional formatting

Copyright © 2025-2026 by Alan M. Marcum, Nescorna Professional.
All rights reserved.

Revision: 4 — 2026-09-30.

Flight sheets use Excel's classic cell-value conditional formatting for every
sensor column with an alarm threshold recorded in the source file:

| Comparison | Excel preset | Fill RGB | Text RGB |
|---|---|---|---|
| Greater than or equal to high alarm | Light Red Fill with Dark Red Text | FFC7CE | 9C0006 |
| Less than or equal to low alarm | Yellow Fill with Dark Yellow Text | FFEB9C | 9C6500 |

The comparisons are inclusive: equality triggers the corresponding format. There is no
rule for an absent threshold or an absent sensor. Present sensor columns with
blank readings still get the relevant rules, but an earlier rule skips blank or
nonnumeric cells so Excel does not treat a missing reading as zero. Rules cover
only sample rows, excluding the header.

Each comparison references the numeric Value cell in Summary column C for the
appropriate source and alarm direction, for example `Summary!$C$38`. The exporter
finds the actual row while writing Summary; it does not assume a fixed row number
or embed a literal threshold in the conditional format. With multiple inputs,
every Flight sheet references its own download's Summary rows, including duplicate
flight numbers. Editing a Summary limit changes the conditional formatting in
Excel. It does not recalculate the stored Limits column or graph alarm lines.

CHT channels share the source CHT alarms, and TIT channels share the source TIT
alarms. Other channels use their own recorded alarms. Battery-voltage thresholds
use the scaled volt values already reported in Summary; cooling-rate low limits
retain their negative source-derived values. Low alarms use the yellow preset,
including the cooling-rate channel.

Combined workbooks show Summary as before. Separate workbooks include a hidden
Summary sheet holding the same source metadata and limit values. Their visible
tabs remain Flight followed by its optional Graph sheet, and the workbook opens
on Flight. Summary can be unhidden in Excel to inspect or edit its limits.

The exporter uses the standard preset RGB colors in a native differential style,
with the fill background explicitly set and no foreground pattern. `openpyxl`
has no selector for Excel's named red/yellow presets, so it writes the equivalent
background-fill and font properties. This follows the background-color style
shown in the [openpyxl conditional-formatting documentation](https://openpyxl.readthedocs.io/en/stable/formatting.html).

At export time, a flight with any reading at or beyond a high/low limit gets a
yellow Flight tab. Each sensor column with such a reading gets red header text.
Blank readings and absent thresholds do not trigger these indicators. Cylinder
and TIT columns are evaluated individually against their source's shared limits.
Other headers retain their existing text color; header fill and bold styling are
preserved. This applies to combined and separate workbooks. The tab and header
colors reflect the exported readings and limits; they do not recalculate when
Summary is edited later.
