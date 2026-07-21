from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_parser import TelemetryParseError, parse_telemetry


class TelemetryParserTests(unittest.TestCase):
    def test_valid_frame(self) -> None:
        value = parse_telemetry(
            "F:1520.5,AX:0.12,AY:0.08,AZ:0.99,U:36.2,S:2"
        )
        self.assertAlmostEqual(value.force_n, 1520.5)
        self.assertAlmostEqual(value.pid_output_percent, 36.2)
        self.assertEqual(value.status, 2)
        self.assertGreaterEqual(value.vibration_g, 0.0)

    def test_unknown_fields_are_ignored(self) -> None:
        value = parse_telemetry(
            "F:100,AX:0,AY:0,AZ:1,U:0,S:0,TEMP:25"
        )
        self.assertEqual(value.force_n, 100)

    def test_missing_field_is_rejected(self) -> None:
        with self.assertRaises(TelemetryParseError):
            parse_telemetry("F:100,AX:0,AY:0,AZ:1,U:0")

    def test_invalid_number_is_rejected(self) -> None:
        with self.assertRaises(TelemetryParseError):
            parse_telemetry("F:error,AX:0,AY:0,AZ:1,U:0,S:0")

    def test_raw_magnitude_mode(self) -> None:
        value = parse_telemetry(
            "F:0,AX:0,AY:0,AZ:1,U:0,S:0", remove_gravity=False
        )
        self.assertAlmostEqual(value.vibration_g, 1.0)


if __name__ == "__main__":
    unittest.main()
