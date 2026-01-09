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
