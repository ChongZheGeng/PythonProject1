"""Parse one telemetry line from the STM32 controller."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(slots=True)
class Telemetry:
    force_n: float
    ax_g: float
    ay_g: float
    az_g: float
    pid_output_percent: float
    status: int
    acceleration_magnitude_g: float
    vibration_g: float


class TelemetryParseError(ValueError):
    """Raised when a telemetry line is incomplete or malformed."""


def parse_telemetry(line: str, *, remove_gravity: bool = True) -> Telemetry:
    """Parse a line such as ``F:1520.5,AX:0.12,AY:0.08,AZ:9.75,U:36.2,S:2``.

    Unknown fields are ignored so the protocol can be extended later. Required
    fields must all be present. ``remove_gravity`` assumes accelerometer values
    use g as the unit and reports ``abs(|a|-1)`` as a simple vibration index.
    """

    text = line.strip()
    if not text:
        raise TelemetryParseError("收到空数据帧")

    fields: dict[str, str] = {}
    for part in text.split(","):
        if ":" not in part:
            raise TelemetryParseError(f"字段缺少冒号: {part!r}")
        key, value = part.split(":", 1)
        key = key.strip().upper()
        value = value.strip()
        if key:
            fields[key] = value

    required = ("F", "AX", "AY", "AZ", "U", "S")
    missing = [key for key in required if key not in fields]
    if missing:
        raise TelemetryParseError(f"缺少字段: {', '.join(missing)}")

    try:
        force_n = float(fields["F"])
        ax_g = float(fields["AX"])
        ay_g = float(fields["AY"])
        az_g = float(fields["AZ"])
        pid_output = float(fields["U"])
        status = int(float(fields["S"]))
    except (TypeError, ValueError) as exc:
        raise TelemetryParseError(f"数值转换失败: {exc}") from exc

    magnitude = sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g)
    vibration = abs(magnitude - 1.0) if remove_gravity else magnitude

    return Telemetry(
        force_n=force_n,
        ax_g=ax_g,
        ay_g=ay_g,
        az_g=az_g,
        pid_output_percent=pid_output,
        status=status,
        acceleration_magnitude_g=magnitude,
        vibration_g=vibration,
    )


if __name__ == "__main__":
    sample = "F:1520.5,AX:0.12,AY:0.08,AZ:0.99,U:36.2,S:2"
    print(parse_telemetry(sample))
