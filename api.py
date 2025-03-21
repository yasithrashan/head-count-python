# api.py
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS 
import threading
import time
from headcount import HeadcountDetector
import os
import io

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000", "https://yourdomain.com"]}})

# Global dictionary to store headcount data for each room
headcount_data = {}

# Background thread to run detections for all cameras
def detection_worker():
    # Map of room IDs to camera IDs
    room_cameras = {
        "3la": 0,  # Laptop camera for testing
        # Add more rooms in the future: "3lb": 1, "3lc": 2, etc.
    }
    
    # Create detectors for each room
    detectors = {}
    for room_id, camera_id in room_cameras.items():
        detectors[room_id] = HeadcountDetector(camera_id=camera_id, confidence=0.5)
    
    while True:
        # Process each room
        for room_id, detector in detectors.items():
            try:
                # Get current frame and count
                count = detector.get_current_count()
                
                # Update the global data
                headcount_data[room_id] = {
                    "count": count,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "room_id": room_id
                }
                
                print(f"Updated count for room {room_id}: {count} people")
            except Exception as e:
                print(f"Error processing room {room_id}: {str(e)}")
        
        # Wait for next update interval (3 minutes)
        time.sleep(5)  # every 5 sec

# API endpoint to get headcount for a specific room
@app.route('/api/headcount/<room_id>', methods=['GET'])
def get_room_headcount(room_id):
    if room_id in headcount_data:
        return jsonify(headcount_data[room_id])
    else:
        return jsonify({"error": f"Room {room_id} not found"}), 404

# API endpoint to get headcount for all rooms
@app.route('/api/headcount', methods=['GET'])
def get_all_headcount():
    return jsonify(list(headcount_data.values()))

# API endpoint to get current headcount with image for a specific room
@app.route('/api/headcount/<room_id>/image', methods=['GET'])
def get_room_headcount_with_image(room_id):
    # Map of room IDs to camera IDs
    room_cameras = {
        "3la": 0,  # Laptop camera for testing
        # Add more rooms in the future: "3lb": 1, "3lc": 2, etc.
    }
    
    if room_id not in room_cameras:
        return jsonify({"error": f"Room {room_id} not found"}), 404
    
    try:
        # Create detector for this room
        detector = HeadcountDetector(camera_id=room_cameras[room_id], confidence=0.5)
        
        # Get current count and image
        count, image_bytes = detector.get_current_count_with_image()
        
        # Update the global data
        headcount_data[room_id] = {
            "count": count,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "room_id": room_id
        }
        
        # Return the image
        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/jpeg',
            download_name=f'headcount_{room_id}.jpg'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Immediate count endpoint (doesn't wait for background worker)
@app.route('/api/headcount/<room_id>/immediate', methods=['GET'])
def get_immediate_headcount(room_id):
    # Map of room IDs to camera IDs
    room_cameras = {
        "3la": 0,  # Laptop camera for testing
        # Add more rooms in the future: "3lb": 1, "3lc": 2, etc.
    }
    
    if room_id not in room_cameras:
        return jsonify({"error": f"Room {room_id} not found"}), 404
    
    try:
        # Create detector for this room
        detector = HeadcountDetector(camera_id=room_cameras[room_id], confidence=0.5)
        
        # Get current count
        count = detector.get_current_count()
        
        # Update the global data
        current_data = {
            "count": count,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "room_id": room_id
        }
        
        # Also update the cached data
        headcount_data[room_id] = current_data
        
        return jsonify(current_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the detection thread
    detection_thread = threading.Thread(target=detection_worker, daemon=True)
    detection_thread.start()
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)