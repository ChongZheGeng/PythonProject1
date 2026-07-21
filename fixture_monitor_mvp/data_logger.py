"""CSV logging for fixture-monitor telemetry."""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from data_parser import Telemetry


class CsvLogger:
    def __init__(self, output_dir: str | Path = "data") -> None:
        self.output_dir = Path(output_dir)
        self._file = None
        self._writer: csv.DictWriter | None = None
        self.current_path: Path | None = None

    @property
    def is_recording(self) -> bool:
        return self._file is not None

    def start(self) -> Path:
        if self.is_recording:
            raise RuntimeError("数据记录已经开始")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_path = self.output_dir / f"fixture_test_{stamp}.csv"
        self._file = self.current_path.open("w", newline="", encoding="utf-8-sig")
        fieldnames = [
            "timestamp",
            "target_force_n",
            "force_n",
            "ax_g",
            "ay_g",
            "az_g",
            "acceleration_magnitude_g",
            "vibration_g",
            "pid_output_percent",
            "status",
        ]
        self._writer = csv.DictWriter(self._file, fieldnames=fieldnames)
        self._writer.writeheader()
        self._file.flush()
        return self.current_path

    def write(self, telemetry: Telemetry, target_force_n: float) -> None:
        if not self.is_recording or self._writer is None:
            return

        row = asdict(telemetry)
        row = {
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "target_force_n": f"{target_force_n:.3f}",
            **row,
        }
        self._writer.writerow(row)
        self._file.flush()

    def stop(self) -> Path | None:
        path = self.current_path
        if self._file is not None:
            self._file.flush()
            self._file.close()
        self._file = None
        self._writer = None
        self.current_path = None
        return path

    def __del__(self) -> None:
        self.stop()
