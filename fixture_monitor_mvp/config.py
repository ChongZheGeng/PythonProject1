"""Configuration values for the fixture monitoring MVP."""

APP_TITLE = "智能夹具测控系统"
DEFAULT_BAUD_RATE = 115200
DEFAULT_TARGET_FORCE_N = 1500.0
DEFAULT_KP = 1.2
DEFAULT_KI = 0.08
DEFAULT_KD = 0.03

FORCE_LOW_N = 1300.0
FORCE_HIGH_N = 1700.0
VIBRATION_LIMIT_G = 0.8

MAX_POINTS = 500
SIMULATION_INTERVAL_MS = 50

# BMI088 mounted on a stationary fixture normally measures about 1 g in total.
# When enabled, the UI displays the absolute deviation from 1 g as a simple
# dynamic-vibration indicator. Disable this if the STM32 already removes gravity.
REMOVE_GRAVITY_FROM_MAGNITUDE = True

STATUS_TEXT = {
    0: "待机",
    1: "夹紧中",
    2: "已稳定",
    3: "松开中",
    4: "急停",
}
