# # headcount.py
# import cv2
# import numpy as np
# from ultralytics import YOLO
# from datetime import datetime
# import os
# import csv

# class HeadcountDetector:
#     def __init__(self, camera_id=0, confidence=0.5):
#         """Initialize the headcount detector with laptop camera"""
#         self.camera_id = camera_id
#         self.confidence = confidence
#         # Load YOLOv8 model (downloads automatically if not present)
#         self.model = YOLO('yolov8n.pt')  # Nano model for speed
#         # Ensure logs directory exists
#         os.makedirs('data/logs', exist_ok=True)
        
#     def run_detection(self, location_name="Classroom", save_interval=5):
#         """Run the headcount detection on webcam feed"""
#         # Initialize video capture from webcam
#         cap = cv2.VideoCapture(self.camera_id)
        
#         if not cap.isOpened():
#             print("Error: Could not access webcam")
#             return
            
#         # Prepare for logging
#         log_file = f'data/logs/{location_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
#         with open(log_file, 'w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(['timestamp', 'count'])
        
#         print(f"Starting headcount detection for {location_name}")
#         print("Press 'q' to quit")
        
#         frame_count = 0
        
#         while True:
#             # Read frame from webcam
#             ret, frame = cap.read()
#             if not ret:
#                 print("Failed to capture frame from camera")
#                 break
                
#             frame_count += 1
            
#             # Only process every few frames to reduce CPU usage
#             if frame_count % 3 == 0:
#                 # Run detection
#                 results = self.model(frame)
                
#                 # Count persons (class 0 in COCO dataset)
#                 person_count = 0
#                 for result in results:
#                     boxes = result.boxes
#                     for box in boxes:
#                         cls = int(box.cls[0])
#                         conf = float(box.conf[0])
                        
#                         # Filter for persons with confidence > threshold
#                         if cls == 0 and conf > self.confidence:
#                             person_count += 1
                            
#                             # Draw bounding box
#                             x1, y1, x2, y2 = map(int, box.xyxy[0])
#                             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
#                 # Add count text to frame
#                 cv2.putText(
#                     frame, 
#                     f"People Count: {person_count}", 
#                     (10, 30), 
#                     cv2.FONT_HERSHEY_SIMPLEX, 
#                     1, 
#                     (0, 0, 255), 
#                     2
#                 )
                
#                 # Log count at regular intervals
#                 if frame_count % (save_interval * 30) == 0:  # Approx every 'save_interval' seconds
#                     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                     with open(log_file, 'a', newline='') as f:
#                         writer = csv.writer(f)
#                         writer.writerow([timestamp, person_count])
#                     print(f"{timestamp}: Detected {person_count} people")
            
#             # Display the frame
#             cv2.imshow("University Headcount System", frame)
            
#             # Break loop if 'q' is pressed
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
                
#         # Clean up
#         cap.release()
#         cv2.destroyAllWindows()
#         print(f"Headcount session ended. Log saved to {log_file}")
#         return log_file

# if __name__ == "__main__":
#     # Run as standalone script
#     detector = HeadcountDetector()
#     detector.run_detection("Testing")


# headcount.py
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import os
import csv
import time

class HeadcountDetector:
    def __init__(self, camera_id=0, confidence=0.5):
        """Initialize the headcount detector with laptop camera"""
        self.camera_id = camera_id
        self.confidence = confidence
        # Load YOLOv8 model (downloads automatically if not present)
        self.model = YOLO('yolov8n.pt')  # Nano model for speed
        # Ensure logs directory exists
        os.makedirs('data/logs', exist_ok=True)
        
    def run_detection(self, location_name="Classroom", save_interval=5):
        """Run the headcount detection on webcam feed"""
        # Initialize video capture from webcam
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print("Error: Could not access webcam")
            return
            
        # Prepare for logging
        log_file = f'data/logs/{location_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'count'])
        
        print(f"Starting headcount detection for {location_name}")
        print("Press 'q' to quit")
        
        frame_count = 0
        
        while True:
            # Read frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame from camera")
                break
                
            frame_count += 1
            
            # Only process every few frames to reduce CPU usage
            if frame_count % 3 == 0:
                # Run detection
                results = self.model(frame)
                
                # Count persons (class 0 in COCO dataset)
                person_count = 0
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Filter for persons with confidence > threshold
                        if cls == 0 and conf > self.confidence:
                            person_count += 1
                            
                            # Draw bounding box
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add count text to frame
                cv2.putText(
                    frame, 
                    f"People Count: {person_count}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 0, 255), 
                    2
                )
                
                # Log count at regular intervals
                if frame_count % (save_interval * 30) == 0:  # Approx every 'save_interval' seconds
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(log_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, person_count])
                    print(f"{timestamp}: Detected {person_count} people")
            
            # Display the frame
            cv2.imshow("University Headcount System", frame)
            
            # Break loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print(f"Headcount session ended. Log saved to {log_file}")
        return log_file
    
    def get_current_count(self):
        """Get the current headcount from a single frame without displaying UI"""
        # Initialize video capture
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            raise Exception(f"Could not access camera {self.camera_id}")
        
        # Try to read a few frames to stabilize camera
        for _ in range(3):
            ret, _ = cap.read()
            if not ret:
                time.sleep(0.1)
        
        # Read a frame for detection
        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise Exception("Failed to capture frame from camera")
        
        # Run detection
        results = self.model(frame)
        
        # Count persons (class 0 in COCO dataset)
        person_count = 0
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Filter for persons with confidence > threshold
                if cls == 0 and conf > self.confidence:
                    person_count += 1
        
        # Clean up
        cap.release()
        
        # Log to console
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp}: API detection - {person_count} people on camera {self.camera_id}")
        
        return person_count
    
    def get_current_count_with_image(self):
        """Get the current headcount and return the annotated image as bytes"""
        # Initialize video capture
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            raise Exception(f"Could not access camera {self.camera_id}")
        
        # Try to read a few frames to stabilize camera
        for _ in range(3):
            ret, _ = cap.read()
            if not ret:
                time.sleep(0.1)
        
        # Read a frame for detection
        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise Exception("Failed to capture frame from camera")
        
        # Run detection
        results = self.model(frame)
        
        # Count persons (class 0 in COCO dataset)
        person_count = 0
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Filter for persons with confidence > threshold
                if cls == 0 and conf > self.confidence:
                    person_count += 1
                    
                    # Draw bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add count text to frame
        cv2.putText(
            frame, 
            f"People Count: {person_count}", 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 0, 255), 
            2
        )
        
        # Convert the image to bytes
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        
        # Clean up
        cap.release()
        
        return person_count, image_bytes

if __name__ == "__main__":
    # Run as standalone script for testing
    detector = HeadcountDetector()
    count = detector.get_current_count()
    print(f"Current count: {count} people")