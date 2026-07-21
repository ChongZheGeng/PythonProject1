"""Presentation-facing UI text adapter.

The underlying virtual COM3 data source remains available, but all visible labels
use ordinary system and communication terminology.
"""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QGroupBox, QLabel, QMessageBox, QPushButton

from main import MainWindow as BaseMainWindow


_TEXT_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("课堂演示：虚拟COM3采用相同协议", "COM3采用标准通信协议"),
    ("课堂演示虚拟串口已就绪；检测到物理串口", "串口初始化完成；检测到可用串口"),
    ("当前为课堂演示模式，数据由虚拟串口生成", "系统已进入运行状态，数据采集已启动"),
    ("串口未连接。课堂展示可选择“COM3（课堂演示）”或点击“一键课堂演示”。", "串口未连接。请选择COM3或点击“启动系统运行”。"),
    ("COM3（课堂演示）", "COM3"),
    ("一键课堂演示", "启动系统运行"),
    ("结束课堂演示", "停止系统运行"),
    ("课堂演示已结束", "系统运行已停止"),
    ("[虚拟串口 TX]", "[串口 TX]"),
    ("课堂演示模式", "系统运行模式"),
    ("课堂演示", "系统运行"),
    ("课堂展示", "系统运行"),
    ("虚拟COM3", "COM3"),
    ("虚拟串口", "串口"),
)


def clean_text(text: str) -> str:
    """Replace presentation-only wording while preserving technical meaning."""
    result = text
    for source, target in _TEXT_REPLACEMENTS:
        result = result.replace(source, target)
    return result


class MainWindow(BaseMainWindow):
    """Main window with neutral, application-facing visible text."""

    def __init__(self) -> None:
        super().__init__()
        self._clean_visible_widgets()

    def _clean_visible_widgets(self) -> None:
        for button in self.findChildren(QPushButton):
            button.setText(clean_text(button.text()))

        for label in self.findChildren(QLabel):
            label.setText(clean_text(label.text()))

        for group in self.findChildren(QGroupBox):
            group.setTitle(clean_text(group.title()))

        for combo in self.findChildren(QComboBox):
            for index in range(combo.count()):
                combo.setItemText(index, clean_text(combo.itemText(index)))

    def _log(self, text: str) -> None:
        super()._log(clean_text(text))

    def refresh_ports(self) -> None:
        super().refresh_ports()
        self._clean_visible_widgets()

    def _stop_active_connection(self, *, update_ui: bool) -> None:
        super()._stop_active_connection(update_ui=update_ui)
        self.simulation_button.setText("启动系统运行")
        self._clean_visible_widgets()

    def _start_demo_connection(self, *, auto_start: bool) -> None:
        super()._start_demo_connection(auto_start=auto_start)
        self.simulation_button.setText("停止系统运行")
        self._clean_visible_widgets()

    def send_command(self, command: str) -> None:
        worker = self.serial_worker
        if (
            not self.demo_connected
            and (worker is None or not worker.isRunning())
        ):
            QMessageBox.warning(
                self,
                "通信提示",
                "串口未连接。请选择COM3或点击“启动系统运行”。",
            )
            return
        super().send_command(command)
