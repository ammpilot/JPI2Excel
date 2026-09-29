"""Revision: 1. Project-owned normalized data and errors."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import errno
import re


class ConversionError(Exception):
    def __init__(self, message, code=errno.EINVAL):
        super().__init__(message)
        self.code = code


class DataError(ConversionError):
    def __init__(self, message):
        super().__init__(message, errno.EILSEQ)


class UnsupportedError(ConversionError):
    def __init__(self, message):
        super().__init__(message, errno.EOPNOTSUPP)


@dataclass
class Flight:
    id: int
    source: Path
    start: datetime
    interval: int
    horsepower: int
    fuel_unit: int
    series: dict[str, list[float | None]]
    elapsed: list[int]
    configuration: list[int]
    engine: int = 1

    @property
    def samples(self):
        return len(self.elapsed)

    @property
    def duration(self):
        return self.elapsed[-1] if self.elapsed else 0

    @property
    def timestamps(self):
        return [self.start + timedelta(seconds=value) for value in self.elapsed]

    @property
    def cylinder_count(self):
        return len({int(code[1:]) for code in self.series if re.fullmatch(r'[EC]\d+', code)})

    @property
    def tit_count(self):
        return sum(bool(re.fullmatch(r'T\d+', code)) for code in self.series)

    @property
    def gps(self):
        return any(code in self.series for code in ('LAT', 'LNG', 'ALT', 'SPD'))


@dataclass
class Download:
    path: Path
    metadata: dict[str, object]
    raw_headers: list[str]
    flights: list[Flight]
    alarms: dict[str, tuple[float | None, float | None]]
    warnings: list[str] = field(default_factory=list)
