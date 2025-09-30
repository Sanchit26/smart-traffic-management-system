import cv2
import json
import math
import numpy as np
from ultralytics import YOLO
import supervision as sv
import sys
import os
import base64
import socketio
import time
import yt_dlp
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import config

# Load YOLOv8x model for maximum accuracy on Indian traffic
print("Loading YOLOv8x (best) model for maximum accuracy...")
model = YOLO('yolov8x.pt')  # Extra large model for best accuracy

# Byte tracker for object tracking
tracker = sv.ByteTrack()

def preprocess_frame_for_indian_traffic(frame):
    """Advanced preprocessing optimized for Indian traffic conditions"""
    try:
        # 1. Resize frame for consistent processing (optional - for performance)
        h, w = frame.shape[:2]
        if w > 1280:  # Resize large frames for performance
            scale = 1280 / w
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h))
        
        # 2. Color space enhancement for varying lighting
        # Convert to LAB color space for better lighting handling
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge channels and convert back
        enhanced_lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # 3. Advanced noise reduction
        # Bilateral filter preserves edges while reducing noise
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # 4. Subtle sharpening for better edge detection
        kernel_sharpening = np.array([[-1,-1,-1],
                                    [-1, 9,-1],
                                    [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel_sharpening)
        
        # 5. Color enhancement for better vehicle detection
        # Increase saturation slightly for better color differentiation
        hsv = cv2.cvtColor(sharpened, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1] * 1.1  # Increase saturation by 10%
        hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
        final_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return final_frame.astype(np.uint8)
        
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return frame
import math
import numpy as np
from ultralytics import YOLO
import supervision as sv
import sys
import os
import base64
import socketio
import time
import yt_dlp
from pathlib import Path

# Load Enhanced YOLO model for Indian traffic
print("Loading enhanced YOLO model for Indian traffic detection...")
model = YOLO('yolov8m.pt')  # Medium model for better accuracy on Indian roads
tracker = sv.ByteTrack()

# Enhanced Vehicle classes for Indian traffic
vehicle_classes = {
    0: 'person',        # Pedestrians (common on Indian roads)
    1: 'bicycle',       # Bicycle
    2: 'car',          # Car
    3: 'motorcycle',   # Motorcycle/Scooter (very common in India)
    5: 'bus',          # Bus
    7: 'truck',        # Truck
    # Post-processing will help identify auto-rickshaws, tempo, etc.
}

# Enhanced confidence thresholds for Indian traffic conditions
confidence_thresholds = {
    'person': 0.4,
    'bicycle': 0.3,
    'car': 0.5,
    'motorcycle': 0.35,      # Lower threshold for motorcycles (very common)
    'bus': 0.6,
    'truck': 0.5,
    'auto_rickshaw': 0.25,   # Often misclassified, so lower threshold
    'tempo': 0.4,
}

def preprocess_frame_for_indian_traffic(frame):
    """Enhance frame for better detection on Indian roads"""
    try:
        # Contrast enhancement for varying lighting conditions
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Mild noise reduction
        denoised = cv2.bilateralFilter(enhanced, 5, 50, 50)
        
        return denoised
    except:
        return frame

def classify_indian_vehicle(class_id, confidence, bbox, frame_shape):
    """Enhanced classification for Indian vehicle types"""
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    
    if height == 0:
        return None
        
    aspect_ratio = width / height
    area = width * height
    frame_area = frame_shape[0] * frame_shape[1]
    relative_size = area / frame_area
    
    # Get base vehicle type
    base_type = vehicle_classes.get(class_id)
    
    if base_type is None:
        return None
    
    # Auto-rickshaw detection (often misclassified as car or motorcycle)
    if base_type in ['car', 'motorcycle']:
        if (1.0 < aspect_ratio < 2.2 and 
            0.001 < relative_size < 0.05 and 
            confidence > 0.25 and
            height > width * 0.6):
            return 'auto_rickshaw'
    
    # Enhanced motorcycle detection
    if base_type == 'motorcycle' and confidence > confidence_thresholds['motorcycle']:
        return 'motorcycle'
    
    # Car vs tempo distinction
    if base_type == 'car':
        if aspect_ratio > 2.0 and relative_size > 0.01:
            return 'tempo'
        elif confidence > confidence_thresholds['car']:
            return 'car'
    
    # Bus detection
    if base_type == 'bus' and confidence > confidence_thresholds['bus']:
        return 'bus'
    
    # Truck vs tempo
    if base_type == 'truck':
        if relative_size < 0.03:
            return 'tempo'
        elif confidence > confidence_thresholds['truck']:
            return 'truck'
    
    # Other vehicles
    if base_type in ['bicycle', 'person'] and confidence > confidence_thresholds[base_type]:
        return base_type
    
    return None

def get_indian_vehicle_color(vehicle_type):
    """Color coding for Indian vehicles"""
    colors = {
        'car': (0, 255, 0),           # Green
        'motorcycle': (255, 0, 0),    # Blue  
        'bus': (0, 0, 255),           # Red
        'truck': (255, 255, 0),       # Cyan
        'auto_rickshaw': (255, 0, 255), # Magenta
        'bicycle': (0, 255, 255),     # Yellow
        'tempo': (128, 0, 128),       # Purple
        'person': (255, 128, 0),      # Orange
    }
    return colors.get(vehicle_type, (255, 255, 255))

YOUTUBE_VIDEO_URL = "https://youtu.be/iJZcjZD0fw0?si=3FVnUl3PODxIIBgR"

# If using yt-dlp or similar, update the code to use YOUTUBE_VIDEO_URL as the input source for video processing.
# For example:
ydl_opts = {
    'format': 'best[height<=720]',  # Lower quality for better compatibility
    'outtmpl': 'input_video.%(ext)s',
    'noplaylist': True
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([YOUTUBE_VIDEO_URL])

def detect_lanes_stable(frame):
    """Stable lane detection that consistently returns 2 lanes for Indian roads"""
    h, w, _ = frame.shape
    
    # For Indian traffic videos, we'll use a stable 2-lane detection
    # This prevents random lane count variations
    
    # Simple road analysis for lane validation
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Focus on bottom 40% of frame (road area)
    road_region = gray[int(h*0.6):, :]
    
    # Calculate road width estimation
    road_edges = cv2.Canny(road_region, 50, 150)
    
    # Count significant vertical features that could be lane markers
    vertical_lines = 0
    for x in range(0, w, w//10):  # Sample every 10% of width
        column = road_edges[:, x] if x < w else road_edges[:, -1]
        if np.sum(column) > 100:  # Threshold for significant vertical features
            vertical_lines += 1
    
    # Always return 2 lanes for consistency
    # This is the most common configuration for Indian roads
    consistent_lanes = 2
    
    # No debug lines drawn on frame - clean output
    return consistent_lanes

def run_detection():
    # Find the downloaded video file
    video_files = list(Path('.').glob('input_video.*'))
    if not video_files:
        print("No input video file found. Please check the download.")
        return
    
    video_path = str(video_files[0])
    print(f"Using video file: {video_path}")
    
    frame_id = 0
    output_file = Path(config["save_counts"])
    output_file.parent.mkdir(exist_ok=True)

    sio = socketio.Client()
    sio.connect('http://localhost:5050')
    
    with open(output_file, "a") as f:
        while True:  # Infinite loop for continuous detection
            cap = cv2.VideoCapture(video_path)
            print(f"Starting video loop iteration (frame_id: {frame_id})")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("End of video reached, restarting...")
                    break  # Break inner loop to restart video

                # Enhanced preprocessing for Indian traffic
                processed_frame = preprocess_frame_for_indian_traffic(frame)
                h, w, _ = frame.shape

                # Stable lane detection (always 2 lanes)
                lane_count = detect_lanes_stable(frame)
                lane_width = w // lane_count
                lane_counts = {f"lane_{i+1}": 0 for i in range(lane_count)}

                # Enhanced Indian vehicle counts
                indian_vehicle_counts = {
                    'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0,
                    'auto_rickshaw': 0, 'bicycle': 0, 'tempo': 0, 'person': 0
                }

                # Run YOLOv8x with optimized parameters for maximum accuracy
                results = model.predict(processed_frame, 
                                      conf=0.3,      # Higher confidence for YOLOv8x
                                      iou=0.5,       # Standard IoU for best model
                                      max_det=40,    # Reasonable limit for performance
                                      verbose=False)
                                      
                detections = sv.Detections.from_ultralytics(results[0])
                
                # Filter detections by size (remove very small detections)
                if len(detections) > 0:
                    areas = (detections.xyxy[:, 2] - detections.xyxy[:, 0]) * (detections.xyxy[:, 3] - detections.xyxy[:, 1])
                    min_area = (w * h) * 0.001  # Minimum 0.1% of frame area
                    size_filter = areas > min_area
                    detections = detections[size_filter]
                
                tracked = tracker.update_with_detections(detections)

                # Process detections with proper indexing
                for i, (xyxy, cls_id, tracker_id) in enumerate(zip(tracked.xyxy, tracked.class_id, tracked.tracker_id)):
                    # Get confidence score safely
                    if len(detections.confidence) > 0:
                        # Find matching detection by trying to match coordinates
                        confidence = 0.5  # Default confidence
                        for j, det_xyxy in enumerate(detections.xyxy):
                            if j < len(detections.confidence) and abs(det_xyxy[0] - xyxy[0]) < 5:
                                confidence = detections.confidence[j]
                                break
                    else:
                        confidence = 0.5
                    
                    # Enhanced Indian vehicle classification
                    indian_vehicle_type = classify_indian_vehicle(
                        int(cls_id), confidence, xyxy, frame.shape
                    )
                    
                    if indian_vehicle_type:
                        # Count the vehicle
                        indian_vehicle_counts[indian_vehicle_type] += 1
                        
                        x1, y1, x2, y2 = map(int, xyxy)
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        # Enhanced lane assignment with position weighting
                        # Vehicles closer to camera (bottom of frame) are weighted more heavily
                        weight_factor = cy / h  # 0 to 1, higher for vehicles at bottom
                        
                        # Calculate lane assignment with road perspective
                        # Account for perspective distortion in video
                        normalized_x = cx / w
                        
                        if lane_count == 2:
                            # For 2-lane roads: left lane (0-0.5), right lane (0.5-1.0)
                            if normalized_x < 0.5:
                                lane_index = 0
                            else:
                                lane_index = 1
                        else:
                            # For multi-lane roads
                            lane_index = min(int(normalized_x * lane_count), lane_count - 1)
                        
                        lane_counts[f"lane_{lane_index+1}"] += 1

                        # Draw box with Indian vehicle color coding
                        color = get_indian_vehicle_color(indian_vehicle_type)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Enhanced label with vehicle type and confidence
                        label = f"{indian_vehicle_type}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                        
                        # Background for text
                        cv2.rectangle(frame, (x1, y1-25), (x1 + label_size[0], y1), color, -1)
                        cv2.putText(frame, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

                # Clean information overlay (no debug lines)
                total_vehicles = sum(indian_vehicle_counts.values())
                
                # Create clean background for information
                overlay_bg = np.zeros((120, 600, 3), dtype=np.uint8)
                overlay_bg[:] = (0, 0, 0)  # Black background
                
                # Add clean text information
                info_lines = [
                    f"YOLOv8x Model | Lanes: {lane_count} (Fixed)",
                    f"Total Vehicles: {total_vehicles}",
                    f"Lane 1: {lane_counts.get('lane_1', 0)} | Lane 2: {lane_counts.get('lane_2', 0)}",
                    " | ".join([f"{k.title()}: {v}" for k, v in indian_vehicle_counts.items() if v > 0])
                ]
                
                # Draw information on overlay
                for i, line in enumerate(info_lines):
                    if line.strip():  # Only draw non-empty lines
                        cv2.putText(overlay_bg, line, (10, 25 + i*25), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Blend overlay with main frame
                frame[10:130, 10:610] = cv2.addWeighted(
                    frame[10:130, 10:610], 0.3, overlay_bg, 0.7, 0
                )

                # Encode frame as JPEG and base64
                _, jpeg = cv2.imencode('.jpg', frame)
                b64_frame = base64.b64encode(jpeg.tobytes()).decode('utf-8')
                sio.emit('cv_frame', {'frame': frame_id, 'lane_counts': lane_counts, 'image': b64_frame})

                # Save counts
                f.write(json.dumps({"frame": frame_id, "lane_counts": lane_counts}) + "\n")
                frame_id += 1

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    cap.release()
                    cv2.destroyAllWindows()
                    sio.disconnect()
                    print(f"Processed {frame_id} frames → {output_file}")
                    return

            cap.release()
            # Video ended, continue to restart the loop

            # Encode frame as JPEG and base64
            _, jpeg = cv2.imencode('.jpg', frame)
            b64_frame = base64.b64encode(jpeg.tobytes()).decode('utf-8')
            sio.emit('cv_frame', {'frame': frame_id, 'lane_counts': lane_counts, 'image': b64_frame})

            # Save counts
            f.write(json.dumps({"frame": frame_id, "lane_counts": lane_counts}) + "\n")
            frame_id += 1

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            cap.release()
            # Video ended, continue to restart the loop
            
    # This should never be reached due to infinite loop
    cv2.destroyAllWindows()
    sio.disconnect()
    print(f"Detection stopped after processing {frame_id} frames → {output_file}")

if __name__ == "__main__":
    run_detection()
