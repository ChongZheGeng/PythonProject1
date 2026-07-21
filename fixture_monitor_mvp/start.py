"""Dependency-aware launcher for the smart fixture monitoring application.

Run this file with any chosen Python interpreter. Missing third-party packages
are installed into that same interpreter before the graphical interface starts.
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path


REQUIRED_IMPORTS = {
    "PySide6": "PySide6",
    "pyqtgraph": "pyqtgraph",
    "serial": "pyserial",
}


def missing_packages() -> list[str]:
    """Return pip package names whose import modules are unavailable."""
    missing: list[str] = []
    for module_name, package_name in REQUIRED_IMPORTS.items():
        if importlib.util.find_spec(module_name) is None:
            missing.append(package_name)
    return missing


def install_dependencies(project_dir: Path) -> bool:
    """Install requirements into the interpreter currently running this file."""
    requirements = project_dir / "requirements.txt"
    if not requirements.exists():
        print(f"[错误] 未找到依赖文件：{requirements}")
        return False

    missing = missing_packages()
    if not missing:
        return True

    print("[提示] 当前 Python 环境缺少：" + ", ".join(missing))
    print(f"[提示] 正在使用解释器安装依赖：{sys.executable}")
    print("[提示] 首次安装可能需要几分钟，请保持网络连接。")

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements),
    ]
    try:
        subprocess.run(command, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"[错误] 依赖安装失败：{exc}")
        print("请在 PowerShell 中手动执行：")
        print(
            f'"{sys.executable}" -m pip install -r "{requirements}"'
        )
        return False

    importlib.invalidate_caches()
    still_missing = missing_packages()
    if still_missing:
        print("[错误] 安装完成后仍无法导入：" + ", ".join(still_missing))
        return False

    print("[完成] 依赖安装成功，正在启动软件……")
    return True


def main() -> int:
    project_dir = Path(__file__).resolve().parent
    if not install_dependencies(project_dir):
        return 1

    # Import only after dependencies are confirmed, so ModuleNotFoundError does
    # not terminate the launcher before the automatic repair can run.
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    import config
    from clean_ui import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_TITLE)
    app.setFont(QFont("Microsoft YaHei", 10))
    window = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
