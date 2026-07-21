"""Background serial communication for the fixture monitor."""

from __future__ import annotations

import threading
import time

import serial
from PySide6.QtCore import QThread, Signal


class SerialWorker(QThread):
    """Read newline-delimited telemetry without blocking the GUI thread."""

    line_received = Signal(str)
    connected_changed = Signal(bool, str)
    error_occurred = Signal(str)

    def __init__(self, port: str, baud_rate: int = 115200, parent=None) -> None:
        super().__init__(parent)
        self.port = port
        self.baud_rate = baud_rate
        self._serial: serial.Serial | None = None
        self._stop_event = threading.Event()
        self._write_lock = threading.Lock()

    def run(self) -> None:
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=0.2,
                write_timeout=0.5,
            )
            self.connected_changed.emit(True, f"已连接 {self.port}")

            while not self._stop_event.is_set():
                try:
                    raw = self._serial.readline()
                    if raw:
                        text = raw.decode("utf-8", errors="replace").strip()
                        if text:
                            self.line_received.emit(text)
                except serial.SerialException as exc:
                    self.error_occurred.emit(f"串口读取失败: {exc}")
                    break
                except OSError as exc:
                    self.error_occurred.emit(f"串口已断开: {exc}")
                    break
                time.sleep(0.001)
        except serial.SerialException as exc:
            self.error_occurred.emit(f"无法打开串口 {self.port}: {exc}")
        finally:
            self._close_serial()
            self.connected_changed.emit(False, "未连接")

    def send_line(self, command: str) -> bool:
        """Send one UTF-8 line. Returns False if the port is unavailable."""
        ser = self._serial
        if ser is None or not ser.is_open:
            self.error_occurred.emit("串口未连接，命令未发送")
            return False

        payload = (command.strip() + "\n").encode("utf-8")
        try:
            with self._write_lock:
                ser.write(payload)
                ser.flush()
            return True
        except (serial.SerialException, OSError) as exc:
            self.error_occurred.emit(f"串口发送失败: {exc}")
            return False

    def stop(self) -> None:
        self._stop_event.set()
        self.wait(1500)
        if self.isRunning():
            self._close_serial()
            self.wait(500)

    def _close_serial(self) -> None:
        ser = self._serial
        self._serial = None
        if ser is not None:
            try:
                if ser.is_open:
                    ser.close()
            except serial.SerialException:
                pass
