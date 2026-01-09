# imu_filter.py
import smbus2
import math
from filterpy.kalman import KalmanFilter
import numpy as np

class IMUStabilizer:
    def __init__(self):
        self.bus = smbus2.SMBus(1)
        self.address = 0x68
        
        # Kalman Filter for gyro drift compensation
        self.kf = KalmanFilter(dim_x=2, dim_z=1)
        self.setup_kalman()
        
        # Initialize MPU6050
        self.init_mpu6050()
    
    def setup_kalman(self):
        self.kf.x = np.array([0., 0.])  # Angle, gyro_bias
        self.kf.F = np.array([[1., -0.01],  # State transition
                             [0., 1.]])
        self.kf.H = np.array([[1., 0.]])   # Measurement function
        self.kf.P *= 1000.                 # Covariance matrix
        self.kf.R = 0.01                   # Measurement noise
        self.kf.Q = np.array([[0.001, 0.], # Process noise
                             [0., 0.003]])
    
    def complementary_filter(self, accel, gyro, dt, alpha=0.98):
        """Fusion of accelerometer and gyroscope"""
        # Accel-based angle
        acc_angle = math.atan2(accel[1], 
                              math.sqrt(accel[0]**2 + accel[2]**2))
        
        # Gyro integration
        gyro_angle = self.kf.x[0] + gyro * dt
        
        # Complementary filter
        angle = alpha * gyro_angle + (1-alpha) * acc_angle
        
        # Kalman update
        self.kf.predict()
        self.kf.update(angle)
        
        return self.kf.x[0]  # Filtered angle
    
    def get_yaw(self):
        """Get current yaw angle from gyroscope"""
        try:
            gyro_z = self.read_mpu6050_gyro()[2]
            accel_data = self.read_mpu6050_accel()
            return self.complementary_filter(accel_data, gyro_z, 0.01)
        except Exception as e:
            print(f"Error reading IMU: {e}")
            return 0.0
    
    def init_mpu6050(self):
        """Initialize MPU6050 sensor"""
        try:
            # Wake up the sensor (clear sleep bit)
            self.bus.write_byte_data(self.address, 0x6B, 0x00)
            print("MPU6050 initialized successfully")
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
    
    def read_mpu6050_accel(self):
        """Read accelerometer data from MPU6050"""
        try:
            # Read accel X, Y, Z (6 bytes: 0x3B-0x40)
            data = self.bus.read_i2c_block_data(self.address, 0x3B, 6)
            accel_x = (data[0] << 8 | data[1]) / 16384.0
            accel_y = (data[2] << 8 | data[3]) / 16384.0
            accel_z = (data[4] << 8 | data[5]) / 16384.0
            return [accel_x, accel_y, accel_z]
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
            return [0, 0, 0]
    
    def read_mpu6050_gyro(self):
        """Read gyroscope data from MPU6050"""
        try:
            # Read gyro X, Y, Z (6 bytes: 0x43-0x48)
            data = self.bus.read_i2c_block_data(self.address, 0x43, 6)
            gyro_x = (data[0] << 8 | data[1]) / 131.0
            gyro_y = (data[2] << 8 | data[3]) / 131.0
            gyro_z = (data[4] << 8 | data[5]) / 131.0
            return [gyro_x, gyro_y, gyro_z]
        except Exception as e:
            print(f"Error reading gyroscope: {e}")
            return [0, 0, 0]
