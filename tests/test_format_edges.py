"""Revision: 2. Focused regressions for dates, fast recording and checksum modes."""
from datetime import datetime
import tempfile
from pathlib import Path
import unittest

from jpi2excel.model import DataError, UnsupportedError
from jpi2excel.reader import read_jpi
from test_parser import synthetic_file, dollar, data_start


def record(payload):
    return bytes(payload + [-sum(payload) % 256])


class EdgeTests(unittest.TestCase):
    def parse(self, raw):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data.JPI'
            path.write_bytes(raw)
            return read_jpi(path)

    def test_midnight_is_valid(self):
        raw = bytearray(synthetic_file())
        offset = data_start(raw)
        raw[offset+12:offset+14] = b'\x00\x00'
        raw[offset+14] = -sum(raw[offset:offset+14]) % 256
        self.assertEqual(self.parse(raw).flights[0].start, datetime(2026,9,17))

    def test_invalid_date_does_not_use_download_time(self):
        raw = bytearray(synthetic_file())
        offset = data_start(raw)
        raw[offset+10:offset+12] = b'\x00\x00'
        raw[offset+14] = -sum(raw[offset:offset+14]) % 256
        with self.assertRaises(DataError):
            self.parse(raw)

    def test_fast_record_transitions_keep_elapsed_seconds(self):
        # MARK starts at 240; +2 sets fast recording, +1 restores normal.
        fast = record([4,4,0,1,0,2])
        normal = record([4,4,0,1,0,1])
        raw = synthetic_file([record([1,1,0,1,0,10]), fast, bytes(4), normal, bytes(4)])
        flight = self.parse(raw).flights[0]
        self.assertEqual(flight.elapsed, [0,2,3,4,6])
        self.assertEqual(flight.series['E1'], [250]*5)

    def test_twin_rejected_explicitly(self):
        raw = synthetic_file().replace(dollar('C,700,63741,32689,1556,306'), dollar('C,760,63741,32689,1556,306'))
        with self.assertRaises(UnsupportedError):
            self.parse(raw)

    def test_xor_checksum_branch(self):
        raw = bytearray(synthetic_file([bytes([1,1,0,1,0,10,11])]))
        old = dollar('C,700,63741,32689,1556,306')
        new = dollar('C,700,63741,32689,1556,295')
        raw = raw.replace(old,new)
        offset = data_start(raw)
        value=0
        for byte in raw[offset:offset+14]:
            value ^= byte
        raw[offset+14]=value
        self.assertEqual(self.parse(raw).flights[0].series['E1'],[250])
