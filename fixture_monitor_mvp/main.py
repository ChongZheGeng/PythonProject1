"""Smart-fixture monitoring and PID-control desktop MVP.

The application supports both a real serial port and a classroom-demo virtual
COM port. Run from this directory with::

    python main.py
"""

from __future__ import annotations

import math
import random
import sys
import time
from collections import deque

import pyqtgraph as pg
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from serial.tools import list_ports

import config
from data_logger import CsvLogger
from data_parser import Telemetry, TelemetryParseError, parse_telemetry
from serial_worker import SerialWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(config.APP_TITLE)
        self.resize(1420, 820)

        self.serial_worker: SerialWorker | None = None
        self.csv_logger = CsvLogger()

        self.start_time = time.monotonic()
        self.simulation_time = 0.0
        self.simulated_force = 0.0
        self.demo_connected = False
        self.demo_state = "idle"
        self.demo_hold_target = 0.0

        self.time_values: deque[float] = deque(maxlen=config.MAX_POINTS)
        self.force_values: deque[float] = deque(maxlen=config.MAX_POINTS)
        self.target_values: deque[float] = deque(maxlen=config.MAX_POINTS)
        self.vibration_values: deque[float] = deque(maxlen=config.MAX_POINTS)

        self.simulation_timer = QTimer(self)
        self.simulation_timer.setInterval(config.SIMULATION_INTERVAL_MS)
        self.simulation_timer.timeout.connect(self._generate_simulation_frame)

        self._build_ui()
        self._connect_ui()
        self.refresh_ports()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        title = QLabel("智能夹具测控系统")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setStyleSheet("color:#0b4f8a; padding:4px;")
        root.addWidget(title)

        subtitle = QLabel("夹紧力闭环控制 · 振动状态监测")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color:#607d8b; padding-bottom:4px;")
        root.addWidget(subtitle)

        body = QHBoxLayout()
        root.addLayout(body, 1)

        body.addWidget(self._build_control_panel(), 0)
        body.addWidget(self._build_chart_panel(), 1)
        body.addWidget(self._build_status_panel(), 0)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumBlockCount(300)
        self.log_box.setPlaceholderText("运行日志与报警信息")
        self.log_box.setMaximumHeight(145)
        root.addWidget(self.log_box)

        self.setStyleSheet(
            """
            QMainWindow { background:#f4f7fb; }
            QGroupBox {
                background:white; border:1px solid #b9cbe0; border-radius:8px;
                margin-top:12px; padding-top:10px; font-weight:600;
            }
            QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 5px; }
            QPushButton { min-height:32px; padding:4px 12px; }
            QDoubleSpinBox, QSpinBox, QComboBox { min-height:28px; }
            """
        )

    def _build_control_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(315)
        layout = QVBoxLayout(panel)

        comm_group = QGroupBox("通信设置")
        comm_form = QFormLayout(comm_group)
        self.port_combo = QComboBox()
        self.baud_spin = QSpinBox()
        self.baud_spin.setRange(1200, 2_000_000)
        self.baud_spin.setValue(config.DEFAULT_BAUD_RATE)

        port_row = QHBoxLayout()
        port_row.addWidget(self.port_combo, 1)
        self.refresh_port_button = QPushButton("刷新")
        port_row.addWidget(self.refresh_port_button)
        comm_form.addRow("串口", port_row)
        comm_form.addRow("波特率", self.baud_spin)

        connect_row = QHBoxLayout()
        self.connect_button = QPushButton("连接")
        self.disconnect_button = QPushButton("断开")
        self.disconnect_button.setEnabled(False)
        connect_row.addWidget(self.connect_button)
        connect_row.addWidget(self.disconnect_button)
        comm_form.addRow(connect_row)

        self.simulation_button = QPushButton("一键课堂演示")
        self.simulation_button.setStyleSheet(
            "background:#e3f2fd;color:#0b4f8a;font-weight:bold;"
        )
        comm_form.addRow(self.simulation_button)
        layout.addWidget(comm_group)

        pid_group = QGroupBox("夹紧力与PID参数")
        pid_form = QFormLayout(pid_group)
        self.target_force_spin = self._double_spin(
            0, 50_000, config.DEFAULT_TARGET_FORCE_N, 1.0, " N"
        )
        self.kp_spin = self._double_spin(0, 10_000, config.DEFAULT_KP, 0.01)
        self.ki_spin = self._double_spin(0, 10_000, config.DEFAULT_KI, 0.01)
        self.kd_spin = self._double_spin(0, 10_000, config.DEFAULT_KD, 0.01)
        pid_form.addRow("目标夹紧力", self.target_force_spin)
        pid_form.addRow("Kp", self.kp_spin)
        pid_form.addRow("Ki", self.ki_spin)
        pid_form.addRow("Kd", self.kd_spin)
        self.send_pid_button = QPushButton("下发PID参数")
        pid_form.addRow(self.send_pid_button)
        layout.addWidget(pid_group)

        command_group = QGroupBox("控制命令")
        command_grid = QGridLayout(command_group)
        self.start_button = QPushButton("启动夹紧")
        self.stop_button = QPushButton("停止控制")
        self.release_button = QPushButton("松开工件")
        self.zero_button = QPushButton("夹紧力调零")
        self.emergency_button = QPushButton("急停")
        self.emergency_button.setStyleSheet(
            "background:#c62828;color:white;font-weight:bold;"
        )
        command_grid.addWidget(self.start_button, 0, 0)
        command_grid.addWidget(self.stop_button, 0, 1)
        command_grid.addWidget(self.release_button, 1, 0)
        command_grid.addWidget(self.zero_button, 1, 1)
        command_grid.addWidget(self.emergency_button, 2, 0, 1, 2)
        layout.addWidget(command_group)

        record_group = QGroupBox("实验数据")
        record_row = QHBoxLayout(record_group)
        self.record_button = QPushButton("开始记录")
        self.stop_record_button = QPushButton("停止记录")
        self.stop_record_button.setEnabled(False)
        record_row.addWidget(self.record_button)
        record_row.addWidget(self.stop_record_button)
        layout.addWidget(record_group)
        layout.addStretch(1)
        return panel

    def _build_chart_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        pg.setConfigOptions(antialias=True)
        self.force_plot = pg.PlotWidget(title="夹紧力实时曲线")
        self.force_plot.showGrid(x=True, y=True, alpha=0.25)
        self.force_plot.setLabel("left", "夹紧力", units="N")
        self.force_plot.setLabel("bottom", "时间", units="s")
        self.force_curve = self.force_plot.plot(
            [], [], pen=pg.mkPen("#1976d2", width=2), name="实际夹紧力"
        )
        self.target_curve = self.force_plot.plot(
            [],
            [],
            pen=pg.mkPen("#ef6c00", width=2, style=Qt.DashLine),
            name="目标夹紧力",
        )
        self.force_plot.addLegend()

        self.vibration_plot = pg.PlotWidget(title="振动指标实时曲线")
        self.vibration_plot.showGrid(x=True, y=True, alpha=0.25)
        self.vibration_plot.setLabel("left", "振动指标", units="g")
        self.vibration_plot.setLabel("bottom", "时间", units="s")
        self.vibration_curve = self.vibration_plot.plot(
            [], [], pen=pg.mkPen("#2e7d32", width=2)
        )

        layout.addWidget(self.force_plot, 1)
        layout.addWidget(self.vibration_plot, 1)
        return panel

    def _build_status_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(290)
        layout = QVBoxLayout(panel)

        status_group = QGroupBox("实时状态")
        grid = QGridLayout(status_group)
        self.connection_label = self._status_value("未连接")
        self.force_label = self._status_value("0.0 N", large=True)
        self.target_label = self._status_value(
            f"{config.DEFAULT_TARGET_FORCE_N:.1f} N"
        )
        self.vibration_label = self._status_value("0.000 g", large=True)
        self.pid_output_label = self._status_value("0.0 %")
        self.clamp_state_label = self._status_value("待机")
        self.vibration_state_label = self._status_value("正常")

        rows = [
            ("通信状态", self.connection_label),
            ("实际夹紧力", self.force_label),
            ("目标夹紧力", self.target_label),
            ("振动指标", self.vibration_label),
            ("PID输出", self.pid_output_label),
            ("夹紧状态", self.clamp_state_label),
            ("振动状态", self.vibration_state_label),
        ]
        for row, (name, value) in enumerate(rows):
            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(value, row, 1)
        layout.addWidget(status_group)

        limits_group = QGroupBox("报警阈值")
        limits_form = QFormLayout(limits_group)
        self.force_low_spin = self._double_spin(
            0, 50_000, config.FORCE_LOW_N, 10, " N"
        )
        self.force_high_spin = self._double_spin(
            0, 50_000, config.FORCE_HIGH_N, 10, " N"
        )
        self.vibration_limit_spin = self._double_spin(
            0, 100, config.VIBRATION_LIMIT_G, 0.05, " g"
        )
        limits_form.addRow("夹紧力下限", self.force_low_spin)
        limits_form.addRow("夹紧力上限", self.force_high_spin)
        limits_form.addRow("振动上限", self.vibration_limit_spin)
        layout.addWidget(limits_group)

        protocol = QGroupBox("通信协议")
        protocol_layout = QVBoxLayout(protocol)
        protocol_text = QLabel(
            "STM32 → 上位机：\n"
            "F:1500,AX:0.1,AY:0.1,AZ:0.99,U:35,S:2\n\n"
            "上位机 → STM32：\n"
            "SET,F,KP,KI,KD / START / STOP /\n"
            "RELEASE / EMERGENCY / ZERO\n\n"
            "课堂演示：虚拟COM3采用相同协议"
        )
        protocol_text.setWordWrap(True)
        protocol_text.setStyleSheet("font-family:Consolas,Microsoft YaHei;")
        protocol_layout.addWidget(protocol_text)
        layout.addWidget(protocol)
        layout.addStretch(1)
        return panel

    @staticmethod
    def _double_spin(
        minimum: float,
        maximum: float,
        value: float,
        step: float,
        suffix: str = "",
    ) -> QDoubleSpinBox:
        control = QDoubleSpinBox()
        control.setRange(minimum, maximum)
        control.setDecimals(3)
        control.setSingleStep(step)
        control.setValue(value)
        control.setSuffix(suffix)
        return control

    @staticmethod
    def _status_value(text: str, *, large: bool = False) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet(
            f"font-size:{'22' if large else '15'}px;"
            "font-weight:bold;color:#163a68;padding:4px;"
        )
        return label

    def _connect_ui(self) -> None:
        self.refresh_port_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.connect_serial)
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        self.simulation_button.clicked.connect(self.toggle_classroom_demo)
        self.send_pid_button.clicked.connect(self.send_pid_parameters)
        self.start_button.clicked.connect(lambda: self.send_command("START"))
        self.stop_button.clicked.connect(lambda: self.send_command("STOP"))
        self.release_button.clicked.connect(lambda: self.send_command("RELEASE"))
        self.emergency_button.clicked.connect(
            lambda: self.send_command("EMERGENCY")
        )
        self.zero_button.clicked.connect(lambda: self.send_command("ZERO"))
        self.record_button.clicked.connect(self.start_recording)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.target_force_spin.valueChanged.connect(
            lambda value: self.target_label.setText(f"{value:.1f} N")
        )

    # ---------- communication ----------
    def refresh_ports(self) -> None:
        current_data = self.port_combo.currentData()
        self.port_combo.clear()

        physical_ports = [port.device for port in list_ports.comports()]
        if config.ENABLE_CLASSROOM_DEMO:
            self.port_combo.addItem(
                config.DEMO_PORT_LABEL, config.DEMO_PORT_DEVICE
            )
        for port in physical_ports:
            self.port_combo.addItem(port, port)

        if current_data is not None:
            index = self.port_combo.findData(current_data)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)

        if config.ENABLE_CLASSROOM_DEMO:
            physical_text = ", ".join(physical_ports) if physical_ports else "无"
            self._log(
                f"课堂演示虚拟串口已就绪；检测到物理串口: {physical_text}"
            )
        else:
            self._log(
                f"发现串口: {', '.join(physical_ports) if physical_ports else '无'}"
            )

    def connect_serial(self) -> None:
        port_id = self.port_combo.currentData()
        port_text = self.port_combo.currentText().strip()
        if not port_text:
            QMessageBox.warning(self, "提示", "未检测到可用串口")
            return

        if port_id == config.DEMO_PORT_DEVICE:
            self._start_demo_connection(auto_start=False)
            return

        self._stop_active_connection(update_ui=False)
        worker = SerialWorker(str(port_id or port_text), self.baud_spin.value(), self)
        worker.line_received.connect(self._handle_raw_line)
        worker.connected_changed.connect(self._handle_connection_state)
        worker.error_occurred.connect(self._log_error)
        self.serial_worker = worker
        worker.start()

    def disconnect_serial(self) -> None:
        self._stop_active_connection(update_ui=True)

    def _stop_active_connection(self, *, update_ui: bool) -> None:
        self.simulation_timer.stop()
        self.demo_connected = False
        self.demo_state = "idle"
        self.demo_hold_target = 0.0
        self.simulation_button.setText("一键课堂演示")

        worker = self.serial_worker
        self.serial_worker = None
        if worker is not None:
            worker.stop()
            worker.deleteLater()

        if update_ui:
            self._handle_connection_state(False, "未连接")

    def _start_demo_connection(self, *, auto_start: bool) -> None:
        self._stop_active_connection(update_ui=False)
        self._reset_series()
        self.start_time = time.monotonic()
        self.simulation_time = 0.0
        self.simulated_force = 0.0
        self.demo_connected = True
        self.demo_state = "clamping" if auto_start else "idle"
        self.demo_hold_target = (
            self.target_force_spin.value() if auto_start else 0.0
        )
        self.simulation_timer.start()
        self.simulation_button.setText("结束课堂演示")
        self._handle_connection_state(True, f"{config.DEMO_PORT_SHORT} 已连接")
        self._log("当前为课堂演示模式，数据由虚拟串口生成")
        if auto_start:
            self._log("[虚拟串口 TX] START")

    def toggle_classroom_demo(self) -> None:
        if self.demo_connected:
            self.disconnect_serial()
            self._log("课堂演示已结束")
            return

        index = self.port_combo.findData(config.DEMO_PORT_DEVICE)
        if index >= 0:
            self.port_combo.setCurrentIndex(index)
        self._start_demo_connection(auto_start=True)

    def send_pid_parameters(self) -> None:
        command = (
            f"SET,{self.target_force_spin.value():.3f},"
            f"{self.kp_spin.value():.6f},"
            f"{self.ki_spin.value():.6f},"
            f"{self.kd_spin.value():.6f}"
        )
        self.send_command(command)

    def send_command(self, command: str) -> None:
        if self.demo_connected:
            self._apply_demo_command(command)
            self._log(f"[虚拟串口 TX] {command}")
            return

        worker = self.serial_worker
        if worker is None or not worker.isRunning():
            QMessageBox.warning(
                self,
                "通信提示",
                "串口未连接。课堂展示可选择“COM3（课堂演示）”或点击“一键课堂演示”。",
            )
            return
        if worker.send_line(command):
            self._log(f"发送: {command}")

    def _apply_demo_command(self, command: str) -> None:
        keyword = command.split(",", 1)[0].strip().upper()
        if keyword == "SET":
            self.demo_hold_target = self.target_force_spin.value()
            if self.demo_state == "holding":
                self.demo_state = "clamping"
        elif keyword == "START":
            self.demo_hold_target = self.target_force_spin.value()
            self.demo_state = "clamping"
            self.clamp_state_label.setText("夹紧中")
        elif keyword == "STOP":
            self.demo_hold_target = self.simulated_force
            self.demo_state = "holding" if self.simulated_force > 1.0 else "idle"
        elif keyword == "RELEASE":
            self.demo_state = "releasing"
            self.clamp_state_label.setText("松开中")
        elif keyword == "EMERGENCY":
            self.demo_state = "emergency"
            self.clamp_state_label.setText("急停")
        elif keyword == "ZERO":
            self.simulated_force = 0.0
            self.demo_hold_target = 0.0
            self.demo_state = "idle"
            self.clamp_state_label.setText("待机")

    def _handle_connection_state(self, connected: bool, message: str) -> None:
        self.connection_label.setText(message)
        self.connection_label.setStyleSheet(
            f"font-weight:bold;color:"
            f"{'#2e7d32' if connected else '#7a8695'};padding:4px;"
        )
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)
        self.port_combo.setEnabled(not connected)
        self.baud_spin.setEnabled(not connected)
        self.refresh_port_button.setEnabled(not connected)
        self._log(message)

    def _handle_raw_line(self, line: str) -> None:
        try:
            telemetry = parse_telemetry(
                line, remove_gravity=config.REMOVE_GRAVITY_FROM_MAGNITUDE
            )
        except TelemetryParseError as exc:
            self._log_error(f"数据帧无效: {exc}; 原始数据={line!r}")
            return
        self._update_telemetry(telemetry)

    # ---------- classroom simulation ----------
    def _generate_simulation_frame(self) -> None:
        dt = config.SIMULATION_INTERVAL_MS / 1000.0
        self.simulation_time += dt
        target = self.target_force_spin.value()

        if self.demo_state == "clamping":
            desired = target
            response_rate = min(
                1.0, dt * (2.0 + min(self.kp_spin.value(), 5.0) * 0.18)
            )
            self.simulated_force += (
                desired - self.simulated_force
            ) * response_rate
            if abs(self.simulated_force - desired) < max(desired * 0.015, 4.0):
                self.demo_state = "holding"
                self.demo_hold_target = desired
        elif self.demo_state == "holding":
            desired = self.demo_hold_target
            self.simulated_force += (
                desired - self.simulated_force
            ) * min(1.0, dt * 1.2)
        elif self.demo_state == "releasing":
            self.simulated_force += (
                0.0 - self.simulated_force
            ) * min(1.0, dt * 3.2)
            if self.simulated_force < 2.0:
                self.simulated_force = 0.0
                self.demo_state = "idle"
        elif self.demo_state == "emergency":
            self.simulated_force += (
                0.0 - self.simulated_force
            ) * min(1.0, dt * 7.0)
            if self.simulated_force < 1.0:
                self.simulated_force = 0.0
        else:
            self.simulated_force += (
                0.0 - self.simulated_force
            ) * min(1.0, dt * 2.0)

        noise_sigma = (
            max(target * 0.002, 0.8)
            if self.demo_state in {"clamping", "holding"}
            else 0.3
        )
        force = max(0.0, self.simulated_force + random.gauss(0, noise_sigma))

        if self.demo_state == "holding":
            vibration_dynamic = (
                0.07
                + 0.025
                * math.sin(2 * math.pi * 7 * self.simulation_time)
            )
            cycle = self.simulation_time % 16.0
            if 11.0 < cycle < 12.2:
                vibration_dynamic += (
                    0.16
                    * abs(
                        math.sin(
                            2 * math.pi * 22 * self.simulation_time
                        )
                    )
                )
        elif self.demo_state == "clamping":
            vibration_dynamic = 0.04
        elif self.demo_state in {"releasing", "emergency"}:
            vibration_dynamic = 0.10
        else:
            vibration_dynamic = 0.015

        ax = random.gauss(0, vibration_dynamic / 3)
        ay = random.gauss(0, vibration_dynamic / 3)
        az = 1.0 + random.gauss(0, vibration_dynamic / 3)

        if self.demo_state == "clamping":
            pid_output = max(
                8.0,
                min(
                    100.0,
                    abs(target - force) / max(target, 1.0) * 100.0 + 18.0,
                ),
            )
            status = 1
        elif self.demo_state == "holding":
            pid_output = 20.0 + random.uniform(-1.2, 1.2)
            status = 2
        elif self.demo_state == "releasing":
            pid_output = 12.0
            status = 3
        elif self.demo_state == "emergency":
            pid_output = 0.0
            status = 4
        else:
            pid_output = 0.0
            status = 0

        line = (
            f"F:{force:.3f},AX:{ax:.5f},AY:{ay:.5f},"
            f"AZ:{az:.5f},U:{pid_output:.3f},S:{status}"
        )
        self._handle_raw_line(line)

    # ---------- data/display ----------
    def _reset_series(self) -> None:
        self.time_values.clear()
        self.force_values.clear()
        self.target_values.clear()
        self.vibration_values.clear()
        self.force_curve.setData([], [])
        self.target_curve.setData([], [])
        self.vibration_curve.setData([], [])

    def _update_telemetry(self, telemetry: Telemetry) -> None:
        elapsed = time.monotonic() - self.start_time
        target = self.target_force_spin.value()
        self.time_values.append(elapsed)
        self.force_values.append(telemetry.force_n)
        self.target_values.append(target)
        self.vibration_values.append(telemetry.vibration_g)

        x = list(self.time_values)
        self.force_curve.setData(x, list(self.force_values))
        self.target_curve.setData(x, list(self.target_values))
        self.vibration_curve.setData(x, list(self.vibration_values))

        self.force_label.setText(f"{telemetry.force_n:.1f} N")
        self.vibration_label.setText(f"{telemetry.vibration_g:.3f} g")
        self.pid_output_label.setText(
            f"{telemetry.pid_output_percent:.1f} %"
        )
        self.clamp_state_label.setText(
            config.STATUS_TEXT.get(
                telemetry.status, f"未知({telemetry.status})"
            )
        )

        self._update_alarm_state(telemetry)
        self.csv_logger.write(telemetry, target)

    def _update_alarm_state(self, telemetry: Telemetry) -> None:
        force_low = self.force_low_spin.value()
        force_high = self.force_high_spin.value()
        vibration_limit = self.vibration_limit_spin.value()

        force_alarm = None
        if telemetry.force_n < force_low and telemetry.status == 2:
            force_alarm = "夹紧力低于下限"
        elif telemetry.force_n > force_high:
            force_alarm = "夹紧力高于上限"

        vibration_alarm = telemetry.vibration_g > vibration_limit
        self.force_label.setStyleSheet(
            f"font-size:22px;font-weight:bold;color:"
            f"{'#c62828' if force_alarm else '#163a68'};padding:4px;"
        )
        self.vibration_state_label.setText(
            "超限" if vibration_alarm else "正常"
        )
        self.vibration_state_label.setStyleSheet(
            f"font-weight:bold;color:"
            f"{'#c62828' if vibration_alarm else '#2e7d32'};padding:4px;"
        )

        if force_alarm:
            self._log_error(force_alarm)
        if vibration_alarm:
            self._log_error(
                f"振动超限: {telemetry.vibration_g:.3f} g > "
                f"{vibration_limit:.3f} g"
            )

    # ---------- logging ----------
    def start_recording(self) -> None:
        try:
            path = self.csv_logger.start()
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(self, "记录失败", str(exc))
            return
        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        self._log(f"开始记录数据: {path}")

    def stop_recording(self) -> None:
        path = self.csv_logger.stop()
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        if path:
            self._log(f"数据已保存: {path}")

    def _log(self, text: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self.log_box.appendPlainText(f"[{stamp}] {text}")

    def _log_error(self, text: str) -> None:
        self._log(f"警告: {text}")

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt API)
        self._stop_active_connection(update_ui=False)
        self.csv_logger.stop()
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_TITLE)
    app.setFont(QFont("Microsoft YaHei", 10))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
