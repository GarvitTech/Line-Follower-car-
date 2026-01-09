# main_controller.py
import time
import json
from motor_controller import HighPerformanceMotorController
from vision_processor import VisionProcessor
from imu_filter import IMUStabilizer
import signal
import sys

class LineFollower:
    def __init__(self):
        print("=== INITIALIZING LINE FOLLOWER ===")
        
        # Load configuration
        try:
            with open('config.json') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("Error: config.json not found!")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: config.json is invalid JSON!")
            sys.exit(1)
        
        # Initialize subsystems
        try:
            self.motors = HighPerformanceMotorController()
            self.vision = VisionProcessor()
            self.imu = IMUStabilizer()
        except Exception as e:
            print(f"Error initializing subsystems: {e}")
            sys.exit(1)
        
        # State variables
        self.running = True
        self.mode = 'line_follow'  # Modes: line_follow, sharp_turn, stop
        
        # Performance monitoring
        self.loop_times = []
        
        # Signal handling for clean shutdown
        signal.signal(signal.SIGINT, self.shutdown)
    
    def control_loop(self):
        print("Starting control loop at 100Hz...")
        last_time = time.time()
        
        while self.running:
            # Timing control - CRITICAL for consistent performance
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Target 100Hz loop rate
            if dt < 0.01:
                time.sleep(0.01 - dt)
                continue
            
            # Get sensor data
            vision_error = self.vision.get_error()
            
            # State machine
            if self.mode == 'line_follow':
                if vision_error is not None:
                    # Calculate PID correction
                    correction = self.motors.apply_pid_ff(vision_error, dt)
                    
                    # Base speed with adaptive scaling
                    base_speed = self.config['base_speed']
                    
                    # Apply correction to motors
                    left_speed = base_speed - correction
                    right_speed = base_speed + correction
                    
                    self.motors.set_motors(left_speed, right_speed)
                
                # Check for sharp turn detection
                if abs(vision_error or 0) > self.config['turn_threshold']:
                    self.mode = 'sharp_turn'
                    turn_dir = 'right' if (vision_error or 0) > 0 else 'left'
                    self.execute_sharp_turn(turn_dir)
            
            # Performance logging
            self.loop_times.append(dt)
            if len(self.loop_times) > 1000:
                avg_loop = sum(self.loop_times) / len(self.loop_times)
                print(f"Avg loop time: {1/avg_loop:.1f}Hz")
                self.loop_times = []
    
    def execute_sharp_turn(self, direction):
        """Professional turn execution with IMU feedback"""
        print(f"Executing {direction} 90° turn")
        
        # Use IMU for precise turn
        start_angle = self.imu.get_yaw()
        target_angle = start_angle + (90 if direction == 'right' else -90)
        
        # Begin turn
        turn_speed = 60
        if direction == 'right':
            self.motors.set_motors(-turn_speed, turn_speed)
        else:
            self.motors.set_motors(turn_speed, -turn_speed)
        
        # Monitor with IMU
        while abs(self.imu.get_yaw() - target_angle) > 5:
            time.sleep(0.001)
        
        # Stop and return to line following
        self.motors.set_motors(0, 0)
        time.sleep(0.1)
        self.mode = 'line_follow'
    
    def shutdown(self, sig, frame):
        print("\nShutting down...")
        try:
            self.running = False
            self.vision.running = False
            self.motors.set_motors(0, 0)
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            sys.exit(0)

if __name__ == "__main__":
    robot = LineFollower()
    robot.control_loop()
