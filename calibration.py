# calibration.py
import time
import numpy as np

class AutoCalibration:
    def __init__(self, motors, vision):
        self.motors = motors
        self.vision = vision
        
    def full_calibration(self):
        print("=== AUTO-CALIBRATION SEQUENCE ===")
        
        try:
            # 1. Find line
            print("Searching for line...")
            self.motors.set_motors(30, 30)
            timeout = time.time() + 10  # 10 second timeout
            while self.vision.get_error() is None:
                if time.time() > timeout:
                    print("Error: Line not found within timeout!")
                    return False
                time.sleep(0.1)
            self.motors.set_motors(0, 0)
        except Exception as e:
            print(f"Error during calibration: {e}")
            self.motors.set_motors(0, 0)
            return False
        
        return True
        
        # 2. Center on line
        print("Centering...")
        for _ in range(50):
            error = self.vision.get_error()
            if error:
                self.motors.set_motors(-error*0.5, error*0.5)
                time.sleep(0.02)
        
        # 3. Measure line characteristics
        print("Measuring line properties...")
        errors = []
        for _ in range(100):
            error = self.vision.get_error()
            if error:
                errors.append(error)
                time.sleep(0.01)
        
        # 4. Calculate optimal PID
        error_std = np.std(errors)
        self.calculate_pid_params(error_std)
        
        print("Calibration complete!")
    
    def calculate_pid_params(self, error_std):
        # Expert heuristic: more noise → less aggressive PID
        if error_std < 10:
            kp, ki, kd = 1.0, 0.02, 0.3
        elif error_std < 20:
            kp, ki, kd = 0.7, 0.01, 0.2
        else:
            kp, ki, kd = 0.4, 0.005, 0.1
        
        print(f"Auto-tuned PID: P={kp}, I={ki}, D={kd}")
        return kp, ki, kd
