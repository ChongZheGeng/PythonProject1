# 智能夹具测控系统上位机（MVP）

这是课程项目的最小可运行版本，采用 **Python + PySide6 + PyQtGraph + PySerial**。

## 已实现功能

- 串口搜索、连接、断开；
- 接收 STM32 的夹紧力、BMI088 三轴加速度、PID 输出和状态；
- 显示夹紧力和振动指标实时曲线；
- 设置目标夹紧力、Kp、Ki、Kd 并下发；
- 发送启动、停止、松开、急停和调零命令；
- 夹紧力及振动阈值报警；
- CSV 数据记录；
- 无硬件时可使用模拟数据完成演示。

## 目录

```text
fixture_monitor_mvp/
├─ main.py             主界面、曲线和业务逻辑
├─ serial_worker.py    后台串口线程
├─ data_parser.py      STM32 数据帧解析
├─ data_logger.py      CSV 数据记录
├─ config.py           默认参数及报警阈值
├─ requirements.txt    Python 依赖
├─ setup_windows.bat   Windows 一键创建环境并安装依赖
├─ run_windows.bat     Windows 一键启动程序
└─ tests/
   └─ test_data_parser.py
```

## 重要：命令应输入在终端，不是 Python Console

`cd`、`pip install`、`python main.py` 都是 **PowerShell/CMD 命令**，不能粘贴到 PyCharm 的 **Python Console**。如果在 Python Console 中输入：

```text
cd fixture_monitor_mvp
```

会得到 `SyntaxError: invalid syntax`，这不是程序代码错误。

在 PyCharm 中请打开：

```text
View → Tool Windows → Terminal
```

然后在底部的 Terminal 中执行命令。也可以直接右键 `fixture_monitor_mvp/main.py`，选择 **Run 'main'**。

## 安装与运行

支持 Python 3.10 或 3.11。

### 方法一：Windows 一键启动（推荐）

在资源管理器中进入 `fixture_monitor_mvp` 文件夹：

1. 首次运行双击 `setup_windows.bat`；
2. 安装完成后双击 `run_windows.bat`。

也可以在 PyCharm Terminal 中执行：

```powershell
cd D:\PythonProject1\fixture_monitor_mvp
.\setup_windows.bat
.\run_windows.bat
```

### 方法二：使用你现有的 PyCharm 解释器

如果当前解释器是：

```text
D:\labview\.venv\Scripts\python.exe
```

请在 **PyCharm Terminal** 中直接执行：

```powershell
D:\labview\.venv\Scripts\python.exe -m pip install -r D:\PythonProject1\fixture_monitor_mvp\requirements.txt
D:\labview\.venv\Scripts\python.exe D:\PythonProject1\fixture_monitor_mvp\main.py
```

不需要在 Python Console 中执行 `cd` 或激活虚拟环境。

### 方法三：手动创建项目虚拟环境

在 PyCharm Terminal 或 PowerShell 中执行：

```powershell
cd D:\PythonProject1\fixture_monitor_mvp
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

这种方式不依赖 `Activate.ps1`，可避免 PowerShell 执行策略问题。

没有 STM32 时，点击 **启动模拟数据** 即可测试界面、实时曲线、报警与 CSV 保存。

## PyCharm 运行配置

推荐设置：

- Script path：`D:\PythonProject1\fixture_monitor_mvp\main.py`
- Working directory：`D:\PythonProject1\fixture_monitor_mvp`
- Python interpreter：`D:\labview\.venv\Scripts\python.exe`，或项目中的 `.venv\Scripts\python.exe`

设置完成后，点击绿色运行按钮即可，不需要手动输入启动命令。

## 通信协议

### STM32 → 上位机

每帧以换行符 `\n` 结束：

```text
F:1520.5,AX:0.12,AY:0.08,AZ:0.99,U:36.2,S:2
```

| 字段 | 含义 | 单位 |
|---|---|---|
| F | 实际夹紧力 | N |
| AX、AY、AZ | BMI088 三轴加速度 | g |
| U | PID 输出 | % |
| S | 系统状态编号 | — |

状态编号：

- `0`：待机
- `1`：夹紧中
- `2`：已稳定
- `3`：松开中
- `4`：急停

程序默认将 `abs(sqrt(AX²+AY²+AZ²)-1)` 作为简单振动指标。如果 STM32 已去除重力分量，请在 `config.py` 中设置：

```python
REMOVE_GRAVITY_FROM_MAGNITUDE = False
```

### 上位机 → STM32

PID 参数：

```text
SET,1500.000,1.200000,0.080000,0.030000
```

控制命令：

```text
START
STOP
RELEASE
EMERGENCY
ZERO
```

所有命令同样以 `\n` 结束。

## CSV 输出

点击“开始记录”后，数据保存在当前目录的 `data/` 文件夹。CSV 使用 `utf-8-sig` 编码，可以直接用 Excel 打开。

## 测试

在 `fixture_monitor_mvp` 目录下执行：

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 后续硬件联调顺序

1. STM32 先周期性发送固定测试帧；
2. 接入 NAU7802 并完成夹紧力调零和标定；
3. 接入 BMI088，确认单位、方向和静态零偏；
4. 验证控制命令；
5. 由小夹紧力开始进行 PID 联调；
6. 最后再启用报警联锁或自动停止。

> 安全提示：上位机只负责参数下发和监控。实时 PID、行程限位、力上限和急停逻辑应在 STM32 内部实现，不能依赖 Windows 软件完成安全保护。
