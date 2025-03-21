# web_app.py
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import cv2
import base64
import json
import os
from datetime import datetime
import threading

# Import your existing modules
from headcount import HeadcountDetector
from analyzer import HeadcountAnalyzer

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable cross-origin requests

# Global variables
detector = None
analyzer = HeadcountAnalyzer()
detection_thread = None
stop_detection = False
current_frame = None
current_count = 0

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start the headcount detection in a separate thread"""
    global detection_thread, stop_detection, detector
    
    if detection_thread and detection_thread.is_alive():
        return jsonify({'success': False, 'message': 'Detection already running'})
    
    try:
        data = request.json
        location = data.get('location', 'Classroom')
        camera_id = int(data.get('camera_id', 0))
        confidence = float(data.get('confidence', 0.5))
        save_interval = int(data.get('save_interval', 5))
        
        # Initialize detector here to ensure it's in the correct thread
        detector = HeadcountDetector(camera_id=camera_id, confidence=confidence)
        
        # Reset the flag
        stop_detection = False
        
        # Start detection in a background thread
        detection_thread = threading.Thread(
            target=run_detection_thread,
            args=(location, camera_id, confidence, save_interval)
        )
        detection_thread.daemon = True
        detection_thread.start()
        
        return jsonify({'success': True, 'message': 'Detection started'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting detection: {str(e)}'})

@app.route('/api/stop_detection', methods=['POST'])
def stop_detection_endpoint():
    """Stop the currently running detection"""
    global stop_detection
    
    if not detection_thread or not detection_thread.is_alive():
        return jsonify({'success': False, 'message': 'No detection running'})
    
    stop_detection = True
    return jsonify({'success': True, 'message': 'Detection stopping...'})

@app.route('/api/current_frame')
def get_current_frame():
    """Get the latest processed frame with detections"""
    global current_frame, current_count
    
    if current_frame is None:
        return jsonify({'success': False, 'message': 'No frame available'})
    
    try:
        # Convert the OpenCV frame to a base64 encoded JPEG
        _, buffer = cv2.imencode('.jpg', current_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'frame': f'data:image/jpeg;base64,{frame_base64}',
            'count': current_count
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error encoding frame: {str(e)}'})

@app.route('/api/logs')
def get_logs():
    """Get a list of available log files"""
    try:
        logs = analyzer.get_available_logs()
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting logs: {str(e)}'})

@app.route('/api/analyze/<log_file>')
def analyze_log(log_file):
    """Generate analysis for a specific log file"""
    # Security check
    if '../' in log_file or not log_file.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Invalid log file'})
    
    try:
        report = analyzer.generate_report(log_file)
        if not report:
            return jsonify({'success': False, 'message': 'Failed to generate report'})
        
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error analyzing log: {str(e)}'})

@app.route('/api/visualize/<log_file>')
def visualize_log(log_file):
    """Generate and return visualization for a log file"""
    # Security check
    if '../' in log_file or not log_file.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Invalid log file'})
    
    try:
        # Generate a unique filename for this visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vis_path = os.path.join('static', 'visualizations', f'{timestamp}_{log_file}.png')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(vis_path), exist_ok=True)
        
        # Generate the visualization
        success = analyzer.visualize_log(log_file, vis_path)
        if not success:
            return jsonify({'success': False, 'message': 'Failed to generate visualization'})
        
        # Return the URL to the visualization
        vis_url = f'/static/visualizations/{os.path.basename(vis_path)}'
        return jsonify({'success': True, 'visualization_url': vis_url})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error visualizing log: {str(e)}'})

def run_detection_thread(location, camera_id, confidence, save_interval):
    """Background thread to run the headcount detection"""
    global current_frame, current_count, stop_detection, detector
    
    try:
        # Initialize video capture
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("Error: Could not access webcam")
            return
            
        # Prepare for logging
        log_file = f'data/logs/{location}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'w', newline='') as f:
            f.write('timestamp,count\n')
        
        print(f"Starting headcount detection for {location}")
        
        frame_count = 0
        
        while not stop_detection:
            # Read frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame from camera")
                break
                
            frame_count += 1
            
            # Only process every few frames to reduce CPU usage
            if frame_count % 3 == 0:
                # Run detection
                results = detector.model(frame)
                
                # Count persons (class 0 in COCO dataset)
                person_count = 0
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Filter for persons with confidence > threshold
                        if cls == 0 and conf > detector.confidence:
                            person_count += 1
                            
                            # Draw bounding box
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Update global variables
                current_count = person_count
                
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
                
                # Update the current frame
                current_frame = frame.copy()
                
                # Log count at regular intervals
                if frame_count % (save_interval * 30) == 0:  # Approx every 'save_interval' seconds
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(log_file, 'a', newline='') as f:
                        f.write(f"{timestamp},{person_count}\n")
                    print(f"{timestamp}: Detected {person_count} people")
        
        # Clean up
        cap.release()
        print(f"Headcount session ended. Log saved to {log_file}")
    except Exception as e:
        print(f"Error in detection thread: {str(e)}")

if __name__ == "__main__":
    try:
        # Make sure the directories exist
        os.makedirs('data/logs', exist_ok=True)
        os.makedirs('static/visualizations', exist_ok=True)
        
        print("Starting web server...")
        
        # Run the Flask app - Use debug=False in production
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error starting web server: {str(e)}")