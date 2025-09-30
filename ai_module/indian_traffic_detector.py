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

# Enhanced Indian Traffic Detection System
class IndianTrafficDetector:
    def __init__(self):
        # Use medium YOLO model for better accuracy (you can upgrade to yolov8l.pt for even better results)
        print("Loading YOLOv8 medium model for enhanced Indian traffic detection...")
        self.model = YOLO('yolov8m.pt')  # Download will happen automatically if not present
        
        # Byte tracker for vehicle tracking
        self.tracker = sv.ByteTrack()
        
        # Indian vehicle classes mapping from COCO classes
        self.coco_to_indian = {
            0: 'person',        # person (pedestrians common in Indian roads)
            1: 'bicycle',       # bicycle
            2: 'car',          # car 
            3: 'motorcycle',   # motorcycle/scooter
            5: 'bus',          # bus
            7: 'truck',        # truck
            # We'll use post-processing to detect auto-rickshaws, tempo, etc.
        }
        
        # Enhanced confidence thresholds for Indian traffic
        self.confidence_thresholds = {
            'person': 0.4,          # Pedestrians
            'bicycle': 0.3,         # Bicycles (lower threshold as they're smaller)
            'car': 0.5,            # Cars
            'motorcycle': 0.35,     # Motorcycles/scooters (very common in India)
            'bus': 0.6,            # Buses
            'truck': 0.5,          # Trucks
            'auto_rickshaw': 0.25,  # Auto-rickshaws (often misclassified)
            'tempo': 0.4,          # Tempo/mini trucks
        }
        
        # Vehicle counting
        self.vehicle_counts = {
            'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0,
            'auto_rickshaw': 0, 'bicycle': 0, 'tempo': 0, 'person': 0
        }
        
        # Frame processing
        self.frame_count = 0
        self.total_frames_processed = 0
        
        # Socket.IO client for backend communication
        self.sio = socketio.Client()
        self.connect_to_backend()
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
    def connect_to_backend(self):
        """Connect to backend server"""
        try:
            self.sio.connect('http://localhost:5050', transports=['polling'])
            print("✅ Connected to backend server for real-time updates")
        except Exception as e:
            print(f"⚠️ Failed to connect to backend: {e}")
            print("Will continue processing without real-time updates")
    
    def download_video(self, url):
        """Download video with Indian traffic optimization"""
        print(f"📥 Downloading video: {url}")
        
        ydl_opts = {
            'format': 'best[height<=720]',  # Limit to 720p for optimal processing speed
            'outtmpl': 'indian_traffic_input.%(ext)s',
            'noplaylist': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            # Find the downloaded video file
            for file in os.listdir('.'):
                if file.startswith('indian_traffic_input'):
                    print(f"✅ Video downloaded: {file}")
                    return file
                    
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            
        return None
    
    def preprocess_frame(self, frame):
        """Enhanced preprocessing for Indian traffic conditions"""
        try:
            # 1. Contrast enhancement (Indian videos often have varying lighting)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # 2. Mild noise reduction
            denoised = cv2.bilateralFilter(enhanced, 5, 50, 50)
            
            # 3. Slight sharpening for better detection
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            return sharpened
            
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return frame
    
    def classify_indian_vehicle(self, class_id, confidence, bbox, frame_shape):
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
        
        # Get base vehicle type from COCO
        base_type = self.coco_to_indian.get(class_id)
        
        if base_type is None:
            return None
        
        # Enhanced classification for Indian context
        
        # Auto-rickshaw detection (often misclassified as car or motorcycle)
        if base_type in ['car', 'motorcycle']:
            # Auto-rickshaws have specific aspect ratio and size characteristics
            if (1.0 < aspect_ratio < 2.2 and 
                0.001 < relative_size < 0.05 and 
                confidence > 0.25):
                # Additional check: auto-rickshaws are usually taller relative to width
                if height > width * 0.6:
                    return 'auto_rickshaw'
        
        # Motorcycle/Scooter detection (very common in India)
        if base_type == 'motorcycle':
            if confidence > self.confidence_thresholds['motorcycle']:
                return 'motorcycle'
        
        # Car detection
        if base_type == 'car':
            # Check if it might be a tempo (small truck)
            if (aspect_ratio > 2.0 and relative_size > 0.01):
                return 'tempo'
            elif confidence > self.confidence_thresholds['car']:
                return 'car'
        
        # Bus detection (larger vehicles)
        if base_type == 'bus':
            if confidence > self.confidence_thresholds['bus']:
                return 'bus'
        
        # Truck detection
        if base_type == 'truck':
            # Distinguish between truck and tempo based on size
            if relative_size < 0.03:
                return 'tempo'
            elif confidence > self.confidence_thresholds['truck']:
                return 'truck'
        
        # Bicycle detection
        if base_type == 'bicycle':
            if confidence > self.confidence_thresholds['bicycle']:
                return 'bicycle'
        
        # Person detection
        if base_type == 'person':
            if confidence > self.confidence_thresholds['person']:
                return 'person'
        
        return None
    
    def get_vehicle_color(self, vehicle_type):
        """Color coding for different Indian vehicles"""
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
    
    def detect_lanes(self, frame):
        """Enhanced lane detection for Indian roads"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Gaussian blur
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blur, 50, 150, apertureSize=3)
            
            # Define region of interest (focus on road area)
            height, width = frame.shape[:2]
            vertices = np.array([[(0, height), (width//2, height//2), 
                                (width, height)]], dtype=np.int32)
            
            mask = np.zeros_like(edges)
            cv2.fillPoly(mask, vertices, 255)
            masked_edges = cv2.bitwise_and(edges, mask)
            
            # Hough line detection
            lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 
                                  threshold=50, minLineLength=50, maxLineGap=10)
            
            # Count lanes based on detected lines
            if lines is not None and len(lines) > 2:
                return min(len(lines) // 10 + 2, 4)  # Estimate 2-4 lanes
            else:
                return 2  # Default to 2 lanes
                
        except Exception as e:
            print(f"Lane detection error: {e}")
            return 2
    
    def process_frame(self, frame):
        """Main frame processing with Indian traffic optimization"""
        # Preprocess frame
        processed_frame = self.preprocess_frame(frame)
        
        # Run YOLO detection with optimized parameters for Indian traffic
        results = self.model(processed_frame, 
                           conf=0.2,      # Lower confidence to catch more vehicles
                           iou=0.4,       # Lower IoU for dense traffic
                           verbose=False)
        
        # Reset counts for this frame
        frame_vehicle_counts = {
            'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0,
            'auto_rickshaw': 0, 'bicycle': 0, 'tempo': 0, 'person': 0
        }
        
        # Process detections
        detections = []
        annotated_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get detection details
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Classify vehicle type for Indian context
                    vehicle_type = self.classify_indian_vehicle(
                        class_id, confidence, [x1, y1, x2, y2], frame.shape
                    )
                    
                    if vehicle_type:
                        frame_vehicle_counts[vehicle_type] += 1
                        
                        # Draw bounding box
                        color = self.get_vehicle_color(vehicle_type)
                        cv2.rectangle(annotated_frame, 
                                    (int(x1), int(y1)), (int(x2), int(y2)), 
                                    color, 2)
                        
                        # Add label with confidence
                        label = f"{vehicle_type}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                        
                        # Background for text
                        cv2.rectangle(annotated_frame,
                                    (int(x1), int(y1-25)),
                                    (int(x1 + label_size[0]), int(y1)),
                                    color, -1)
                        
                        # Text
                        cv2.putText(annotated_frame, label,
                                  (int(x1), int(y1-5)),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        
                        detections.append({
                            'type': vehicle_type,
                            'confidence': float(confidence),
                            'bbox': [float(x1), float(y1), float(x2), float(y2)]
                        })
        
        # Lane detection and assignment
        num_lanes = self.detect_lanes(frame)
        lane_counts = {f'lane_{i+1}': 0 for i in range(num_lanes)}
        
        # Assign vehicles to lanes based on x-coordinate
        frame_width = frame.shape[1]
        for detection in detections:
            center_x = (detection['bbox'][0] + detection['bbox'][2]) / 2
            lane_index = int((center_x / frame_width) * num_lanes)
            lane_index = max(0, min(lane_index, num_lanes - 1))
            lane_counts[f'lane_{lane_index + 1}'] += 1
        
        # Update cumulative counts
        for vehicle_type, count in frame_vehicle_counts.items():
            self.vehicle_counts[vehicle_type] += count
        
        # Add statistics overlay
        self.add_statistics_overlay(annotated_frame, frame_vehicle_counts, lane_counts)
        
        return annotated_frame, frame_vehicle_counts, lane_counts, detections
    
    def add_statistics_overlay(self, frame, vehicle_counts, lane_counts):
        """Add statistics overlay to the frame"""
        y_offset = 30
        
        # Background for statistics
        cv2.rectangle(frame, (10, 10), (400, 250), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (400, 250), (255, 255, 255), 2)
        
        # Title
        cv2.putText(frame, "Indian Traffic Detection", (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Vehicle counts
        y_offset = 60
        total_vehicles = sum(vehicle_counts.values())
        cv2.putText(frame, f"Total Vehicles: {total_vehicles}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 25
        
        for vehicle_type, count in vehicle_counts.items():
            if count > 0:
                color = self.get_vehicle_color(vehicle_type)
                cv2.putText(frame, f"{vehicle_type.title()}: {count}", (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                y_offset += 20
        
        # Lane counts
        y_offset += 10
        cv2.putText(frame, "Lane Distribution:", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        for lane, count in lane_counts.items():
            cv2.putText(frame, f"{lane}: {count}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            y_offset += 15
    
    def send_detection_data(self, frame, vehicle_counts, lane_counts, detections):
        """Send detection data to backend"""
        try:
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare comprehensive data
            data = {
                'frame': self.frame_count,
                'image': frame_base64,
                'vehicle_counts': vehicle_counts,
                'lane_counts': lane_counts,
                'total_vehicles': sum(vehicle_counts.values()),
                'detections': detections,
                'timestamp': time.time(),
                'detection_type': 'indian_traffic_enhanced',
                'model': 'yolov8m_indian_optimized'
            }
            
            # Send to backend via Socket.IO
            if self.sio.connected:
                self.sio.emit('cv_frame', data)
            
        except Exception as e:
            print(f"Error sending data: {e}")
    
    def run_detection(self, video_url):
        """Main detection loop"""
        # Download video
        video_file = self.download_video(video_url)
        if not video_file:
            print("❌ Failed to download video")
            return
        
        print(f"🚀 Starting Indian traffic detection on {video_file}")
        print("🎯 Optimized for: Cars, Motorcycles, Auto-rickshaws, Buses, Trucks, Tempo, Bicycles")
        
        # Open video
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            print("❌ Error opening video file")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"📹 Video: {fps} FPS, {frame_count_total} frames")
        
        # Detection loop
        while True:
            ret, frame = cap.read()
            
            if not ret:
                # Restart video for continuous loop
                print("🔄 Restarting video for continuous detection...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.frame_count = 0
                continue
            
            self.frame_count += 1
            self.total_frames_processed += 1
            
            # Process every 2nd frame for better performance
            if self.frame_count % 2 == 0:
                try:
                    # Process frame
                    annotated_frame, vehicle_counts, lane_counts, detections = self.process_frame(frame)
                    
                    # Send data to backend
                    self.send_detection_data(annotated_frame, vehicle_counts, lane_counts, detections)
                    
                    # Print progress
                    if self.frame_count % 60 == 0:  # Every 2 seconds at 30fps
                        total_vehicles = sum(vehicle_counts.values())
                        print(f"🚗 Frame {self.frame_count}: {total_vehicles} vehicles detected")
                        if vehicle_counts['auto_rickshaw'] > 0:
                            print(f"   🛺 Auto-rickshaws: {vehicle_counts['auto_rickshaw']}")
                        if vehicle_counts['motorcycle'] > 0:
                            print(f"   🏍️ Motorcycles: {vehicle_counts['motorcycle']}")
                
                except Exception as e:
                    print(f"Error processing frame {self.frame_count}: {e}")
            
            # Control frame rate (30 FPS)
            time.sleep(1/30)


def main():
    """Main function"""
    print("🇮🇳 Enhanced Indian Traffic Detection System")
    print("=" * 50)
    
    # Initialize detector
    detector = IndianTrafficDetector()
    
    # Video URL - use your Indian traffic video
    video_url = "https://youtu.be/iJZcjZD0fw0?si=3FVnUl3PODxIIBgR"
    
    try:
        # Start detection
        detector.run_detection(video_url)
        
    except KeyboardInterrupt:
        print("\n⏹️ Detection stopped by user")
        print(f"📊 Total frames processed: {detector.total_frames_processed}")
        print("🙏 Thank you for using Indian Traffic Detection System")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()