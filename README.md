# Headcount ML Project

A Python-based machine learning project for detecting and counting people in rooms using computer vision.

## Project Overview

This project uses computer vision and machine learning to detect and count people in different rooms through camera feeds. The system provides real-time headcount data through a Flask API.

## Directory Structure

```
├── __pycache__
├── config
├── data
│   └── logs
├── static
│   └── visualizations
├── templates
├── venv
├── analyzer.py
├── api.py
├── app.py
├── headcount.py
├── requirements.txt
├── web_app.py
└── yolov8n.pt
```

## Installation

1. Clone this repository:
   ```
   git clone https:https://github.com/yasithrashan2003/Head-Count-Python.git
   cd headcount-ml-project
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   For the API dependencies, install:
   ```
   pip install flask flask-cors
   ```

## Setup

Make sure you have a camera connected to your system. The default configuration uses your primary camera (index 0).

## Usage

1. Start the API server:
   ```
   python api.py
   ```
   This will start the Flask server on http://localhost:5000

2. API Endpoints:
   - Get headcount for all rooms: `GET /api/headcount`
   - Get headcount for a specific room: `GET /api/headcount/<room_id>`
   - Get immediate headcount for a specific room: `GET /api/headcount/<room_id>/immediate`
   - Get headcount with image for a specific room: `GET /api/headcount/<room_id>/image`

## Configuration

The system is configured to monitor the following rooms:
- "3la": Camera ID 0 (default webcam)

You can add more rooms by updating the `room_cameras` dictionary in the `api.py` file.

## Requirements

The project requires the following libraries as specified in requirements.txt:
```
ultralytics
opencv-python
numpy
pandas
matplotlib
```

Additionally, the API requires:
- Flask
- Flask-CORS

## Notes

- The detection runs in a background thread that updates every 5 seconds.
- The confidence threshold for detection is set to 0.5 by default.
- Cross-origin requests are allowed from specific origins (localhost:5173, localhost:3000, yourdomain.com).

## License

[Your License Information]

## Contact

[Your Contact Information]
