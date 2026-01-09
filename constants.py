# constants.py - All magic numbers and configuration values

# Motor GPIO Pins (BCM numbering)
LEFT_PWM_PIN = 13
LEFT_IN1_PIN = 19
LEFT_IN2_PIN = 26
RIGHT_PWM_PIN = 12
RIGHT_IN1_PIN = 20
RIGHT_IN2_PIN = 21

# PWM Configuration
PWM_FREQUENCY = 20000  # 20kHz for silent operation
DEFAULT_LOOP_FREQUENCY = 100  # Hz

# Camera Configuration
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 60
ROI_Y = 180  # Look ahead point
ROI_HEIGHT = 20

# IMU Configuration
MPU6050_ADDRESS = 0x68
MPU6050_POWER_REG = 0x6B
MPU6050_ACCEL_REG = 0x3B
MPU6050_GYRO_REG = 0x43
ACCEL_SCALE = 16384.0
GYRO_SCALE = 131.0

# Motor Speed Limits
MAX_SPEED = 100
MIN_SPEED = -100

# Calibration Timeouts
CALIBRATION_TIMEOUT = 10  # seconds
LINE_SEARCH_TIMEOUT = 10  # seconds

# Vision Processing
FRAME_QUEUE_SIZE = 2
ADAPTIVE_THRESHOLD_BLOCK_SIZE = 11
ADAPTIVE_THRESHOLD_C = 2

# Turn Control
SHARP_TURN_ANGLE = 90  # degrees
SHARP_TURN_TOLERANCE = 5  # degrees
