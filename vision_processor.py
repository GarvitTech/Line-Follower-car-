# vision_processor.py
import cv2
import numpy as np
from threading import Thread
import queue

class VisionProcessor:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        # OPTIMIZED settings for speed
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.camera.set(cv2.CAP_PROP_FPS, 60)
        
        # ROI (Region of Interest)
        self.roi_y = 180  # Look ahead point
        self.roi_height = 20
        
        # Processing pipeline
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = True
        self.process_thread = Thread(target=self.process_frames)
        self.process_thread.start()
    
    def process_frames(self):
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # 1. Crop ROI (critical for speed)
            roi = frame[self.roi_y:self.roi_y+self.roi_height, :]
            
            # 2. Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # 3. Adaptive threshold (handles lighting changes)
            binary = cv2.adaptiveThreshold(gray, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # 4. Calculate line position using centroid
            nonzero = binary.nonzero()
            if len(nonzero[1]) > 0:
                line_center = int(np.mean(nonzero[1]))
                error = line_center - binary.shape[1]//2
                self.frame_queue.put(error)
    
    def get_error(self):
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
