"""Revision: 2. Native Excel flight graphs styled from CanonicalGraph.xlsx."""
from colorsys import hsv_to_rgb
from math import ceil, floor, log10
import re

from openpyxl.chart import Reference, ScatterChart, Series
from openpyxl.chart.axis import ChartLines
from openpyxl.chart.data_source import AxDataSource, NumData, NumDataSource, NumVal
from openpyxl.chart.series import SeriesLabel, XYSeries
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor
from openpyxl.drawing.text import CharacterProperties, Font, Paragraph, ParagraphProperties


CYLINDER_COLORS = ('FFC000', '00B050', '00B0F0', '0070C0', '7030A0', '945200',
                   'E97132', 'D86ECC', '008080', '808000', 'A64D79', '5C677D')
NAVY = '002060'


def cylinder_color(number):
    if number <= len(CYLINDER_COLORS):
        return CYLINDER_COLORS[number - 1]
    # Deterministic additional hues, keyed by cylinder rather than series order.
    rgb = hsv_to_rgb((number * 0.61803398875) % 1, 0.65, 0.72)
    return ''.join(f'{round(component * 255):02X}' for component in rgb)


def text_properties(size=9, face='Calibri'):
    return CharacterProperties(sz=size * 100, b=False, i=False,
                               latin=Font(typeface=face), solidFill='595959')


def rich_text():
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=text_properties()),
                                 endParaRPr=text_properties())])


def style_title(title, size):
    title.overlay = False
    for paragraph in title.tx.rich.p:
        paragraph.pPr = ParagraphProperties(defRPr=text_properties(size, 'Cambria'))
        for run in paragraph.r:
            run.rPr = text_properties(size, 'Cambria')


def style_axis(axis, title, position, minimum, maximum):
    axis.title = title
    if title is not None:
        style_title(axis.title, 10)
    axis.axPos = position
    axis.scaling.min = minimum
    axis.scaling.max = maximum
    axis.delete = False
    axis.numFmt = '#,##0' if position == 'b' else '0'
    if position == 'b':
        axis.numFmt.sourceLinked = False
    axis.tickLblPos = 'nextTo'
    axis.majorTickMark = 'out' if position == 'r' else 'cross' if position == 'b' else 'none'
    axis.minorTickMark = 'none'
    axis.txPr = rich_text()
    axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    axis.majorGridlines = None
    axis.crosses = 'max' if position == 'r' else 'min'
    if position == 'l':
        axis.majorGridlines = ChartLines(spPr=GraphicalProperties(
            ln=LineProperties(w=9525, solidFill='D9D9D9')))
    elif position == 'b':
        axis.spPr = GraphicalProperties(ln=LineProperties(w=9525, solidFill='D9D9D9'))


def number_data(values):
    # Preserve absent samples as gaps and keep indices aligned with DeltaT.
    return NumData(formatCode='General', ptCount=len(values),
                   pt=[NumVal(idx=index, v=value) for index, value in enumerate(values)
                       if value is not None])


def style_series(series, color, *, dashed=False, width=28575):
    series.graphicalProperties.line = LineProperties(
        solidFill=color, w=width, cap='rnd', round=True,
        prstDash='sysDash' if dashed else 'solid')
    series.marker.symbol = 'none'
    series.smooth = False


def data_series(sheet, flight, code, column, color, *, dashed=False):
    series = Series(Reference(sheet, min_col=column, min_row=1, max_row=flight.samples + 1),
                    xvalues=Reference(sheet, min_col=2, min_row=2, max_row=flight.samples + 1),
                    title_from_data=True)
    series.xVal.numRef.numCache = number_data(flight.elapsed)
    series.yVal.numRef.numCache = number_data(flight.series[code])
    style_series(series, color, dashed=dashed)
    return series


def time_step(duration):
    """Readable numeric ticks with roughly 10–20 labels across the plot."""
    target = max(1, duration / 15)
    scale = 10 ** floor(log10(target))
    return next(multiplier * scale for multiplier in (1, 2, 5, 10)
                if multiplier * scale >= target)


def add_graphs(workbook, sheet, flight, download, columns):
    """Insert the paired graph sheet; return nonfatal chart-omission warnings."""
    graph = workbook.create_sheet(sheet.title.replace('Flight ', 'Graph ', 1))
    graph.sheet_view.showGridLines = False
    graph.sheet_format.baseColWidth = 10
    graph.sheet_format.defaultRowHeight = 15
    warnings = []
    present = {code for code, values in flight.series.items()
               if any(value is not None for value in values)}
    x_max = max(1, flight.duration)  # Excel requires a nonzero axis span.
    for index, (name, pattern, extra, alarm, secondary_code, padding, rounding) in enumerate((
            ('Exhaust Temperatures', r'[ET]\d+', (), 'TIT', 'FF', 100, 100),
            ('Cylinder Temperatures', r'C\d+', ('OILT',), 'CHT', 'RPM', 25, 50))):
        codes = [code for code in columns if code in present
                 and (re.fullmatch(pattern, code) or code in extra)]
        if not codes:
            warnings.append(f'Flight {flight.id}: omitted {name} graph: no temperature data')
            continue
        values = [value for code in codes for value in flight.series[code] if value is not None]
        threshold = download.alarms.get(alarm, (None, None))[1]
        if threshold is not None:
            values.append(threshold)
        chart = ScatterChart(scatterStyle='line')
        chart.title = f'Flight {flight.id} {name}'
        style_title(chart.title, 14)
        chart.display_blanks = 'gap'
        chart.legend.position = 'b'
        chart.legend.overlay = False
        chart.legend.txPr = rich_text()
        chart.graphical_properties = GraphicalProperties(solidFill='FFFFFF',
                                                         ln=LineProperties(noFill=True))
        chart.x_axis.axId, chart.y_axis.axId = 10, 20
        chart.x_axis.crossAx, chart.y_axis.crossAx = 20, 10
        style_axis(chart.x_axis, 'Time (seconds)', 'b', 0, x_max)
        chart.x_axis.majorUnit = time_step(x_max)
        chart.x_axis.minorUnit = chart.x_axis.majorUnit / 2
        style_axis(chart.y_axis, f"Temperature, º{download.metadata['Engine temperature units']}",
                   'l', floor(min(values) / 100) * 100,
                   ceil((max(values) + padding) / rounding) * rounding)
        for code in codes:
            color = cylinder_color(int(code[1:])) if re.fullmatch(r'[EC]\d+', code) else NAVY
            chart.series.append(data_series(sheet, flight, code, columns[code], color))
        if threshold is not None:
            limit = XYSeries(tx=SeriesLabel(v=f'{alarm} Limit'),
                             xVal=AxDataSource(numLit=number_data([0, x_max])),
                             yVal=NumDataSource(numLit=number_data([threshold, threshold])))
            style_series(limit, 'FF0000', width=19050)  # two pixels, 96 dpi
            chart.series.append(limit)
        if secondary_code in present:
            secondary = ScatterChart(scatterStyle='line')
            secondary.x_axis.axId, secondary.y_axis.axId = 30, 40
            secondary.x_axis.crossAx, secondary.y_axis.crossAx = 40, 30
            # Excel can display a title even when its axis is deleted. Give
            # only the primary time axis a title and visible tick labels.
            style_axis(secondary.x_axis, None, 'b', 0, x_max)
            secondary.x_axis.delete = True
            secondary.x_axis.tickLblPos = 'none'
            secondary.x_axis.majorTickMark = 'none'
            secondary.x_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
            values = [value for value in flight.series[secondary_code] if value is not None]
            if secondary_code == 'FF':
                unit = download.metadata['Fuel flow units']
                unit = {'US gallons/hour': 'gph'}.get(unit, unit)
                axis_title = f'Fuel Flow, {unit}'
                minimum, maximum = 1, max(2, ceil(max(values) + 1))
            else:
                axis_title = 'Engine Speed, RPM'
                minimum = floor(min(values) / 100) * 100
                maximum = ceil((max(values) + 100) / 100) * 100
            style_axis(secondary.y_axis, axis_title, 'r', minimum, maximum)
            secondary.series.append(data_series(sheet, flight, secondary_code,
                                                 columns[secondary_code], NAVY, dashed=True))
            chart += secondary
        # Same two-cell placement as the reference: B2 and B52, 48 rows high.
        row, offset = (1, 6350) if index == 0 else (51, 25400)
        chart.anchor = TwoCellAnchor(
            _from=AnchorMarker(col=1, row=row, rowOff=offset),
            to=AnchorMarker(col=18, colOff=596900, row=row + 48, rowOff=offset))
        graph.add_chart(chart)
    return warnings
