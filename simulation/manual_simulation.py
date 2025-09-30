#!/usr/bin/env python3
"""
Manual Traffic Simulation - Designed for Dashboard Control
This simulation is specifically built to be controlled from the dashboard manual control interface.
It provides a simplified, responsive traffic simulation that prioritizes real-time control.
"""

import pygame
import random
import time
import json
import os
import sys
import math
from collections import deque

# Socket.IO for dashboard communication
try:
    import socketio
except ImportError:
    print("⚠️ python-socketio not installed. Install with: pip install python-socketio")
    socketio = None

# Constants for simulation
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Traffic signal states
SIGNAL_RED = "red"
SIGNAL_YELLOW = "yellow"
SIGNAL_GREEN = "green"

# Direction constants
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

DIRECTION_NAMES = {NORTH: "North", EAST: "East", SOUTH: "South", WEST: "West"}
DIRECTION_KEYS = {"North": NORTH, "East": EAST, "South": SOUTH, "West": WEST}
DIRECTION_IMAGE_NAMES = {NORTH: "up", EAST: "right", SOUTH: "down", WEST: "left"}

# Base directory for assets
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def asset_path(*parts):
    """Get path to asset file"""
    return os.path.join(SCRIPT_DIR, "images", *parts)

# Vehicle types
VEHICLE_TYPES = ["car", "bus", "truck", "bike", "rickshaw", "ambulance"]
VEHICLE_COLORS = {
    "car": (200, 100, 100),
    "bus": (100, 200, 100),
    "truck": (100, 100, 200),
    "bike": (200, 200, 100),
    "rickshaw": (200, 100, 200),
    "ambulance": (255, 255, 255)
}

# Vehicle speeds (pixels per frame)
VEHICLE_SPEEDS = {
    "car": 2.5,
    "bus": 2.0,
    "truck": 1.8,
    "bike": 3.0,
    "rickshaw": 2.2,
    "ambulance": 3.5
}

# Intersection coordinates
INTERSECTION_CENTER_X = 700
INTERSECTION_CENTER_Y = 400
INTERSECTION_SIZE = 120

# Lane positions for each direction
LANE_POSITIONS = {
    NORTH: [
        (INTERSECTION_CENTER_X - 40, INTERSECTION_CENTER_Y + INTERSECTION_SIZE//2, 0, -1),  # Lane 1
        (INTERSECTION_CENTER_X - 20, INTERSECTION_CENTER_Y + INTERSECTION_SIZE//2, 0, -1),  # Lane 2
    ],
    SOUTH: [
        (INTERSECTION_CENTER_X + 20, INTERSECTION_CENTER_Y - INTERSECTION_SIZE//2, 0, 1),   # Lane 1
        (INTERSECTION_CENTER_X + 40, INTERSECTION_CENTER_Y - INTERSECTION_SIZE//2, 0, 1),   # Lane 2
    ],
    EAST: [
        (INTERSECTION_CENTER_X - INTERSECTION_SIZE//2, INTERSECTION_CENTER_Y - 40, 1, 0),   # Lane 1
        (INTERSECTION_CENTER_X - INTERSECTION_SIZE//2, INTERSECTION_CENTER_Y - 20, 1, 0),   # Lane 2
    ],
    WEST: [
        (INTERSECTION_CENTER_X + INTERSECTION_SIZE//2, INTERSECTION_CENTER_Y + 20, -1, 0),  # Lane 1
        (INTERSECTION_CENTER_X + INTERSECTION_SIZE//2, INTERSECTION_CENTER_Y + 40, -1, 0),  # Lane 2
    ]
}

# Stop lines for traffic signals
STOP_LINES = {
    NORTH: INTERSECTION_CENTER_Y + INTERSECTION_SIZE//2 + 10,
    SOUTH: INTERSECTION_CENTER_Y - INTERSECTION_SIZE//2 - 10,
    EAST: INTERSECTION_CENTER_X - INTERSECTION_SIZE//2 - 10,
    WEST: INTERSECTION_CENTER_X + INTERSECTION_SIZE//2 + 10
}

class ManualControlClient:
    """Handles communication with dashboard backend for manual control"""
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.socket = None
        self.connected = False
        self.manual_mode = False
        
        if socketio:
            self.setup_connection()
    
    def setup_connection(self):
        """Initialize Socket.IO connection to dashboard backend"""
        try:
            self.socket = socketio.Client()
            
            # Event handlers
            self.socket.on('connect', self.on_connect)
            self.socket.on('disconnect', self.on_disconnect)
            self.socket.on('simulation_manual_signal', self.on_manual_signal)
            self.socket.on('simulation_manual_mode', self.on_manual_mode_toggle)
            
            # Connect to dashboard backend
            self.socket.connect('http://localhost:5050', transports=['polling'])
            
        except Exception as e:
            print(f"❌ Failed to connect to dashboard: {e}")
            self.connected = False
    
    def on_connect(self):
        print("🎛️ Manual simulation connected to dashboard")
        self.connected = True
        self.broadcast_signal_state()
    
    def on_disconnect(self):
        print("🎛️ Manual simulation disconnected from dashboard")
        self.connected = False
    
    def on_manual_signal(self, data):
        """Handle manual signal change from dashboard"""
        if not self.manual_mode:
            return
            
        signal_id = data.get('signal_id')
        new_state = data.get('new_state')
        
        print(f"🚦 Manual signal change: Signal {signal_id} -> {new_state}")
        
        # Convert signal_id to direction
        if signal_id == '0':  # North
            direction = NORTH
        elif signal_id == '1':  # East
            direction = EAST
        elif signal_id == '2':  # South
            direction = SOUTH
        elif signal_id == '3':  # West
            direction = WEST
        else:
            return
        
        # Update signal state
        self.simulation.set_signal_state(direction, new_state)
        self.broadcast_signal_state()
    
    def on_manual_mode_toggle(self, data):
        """Handle manual mode toggle from dashboard"""
        self.manual_mode = data.get('manual_mode', False)
        print(f"🎛️ Manual mode: {'ON' if self.manual_mode else 'OFF'}")
        self.broadcast_signal_state()
    
    def broadcast_signal_state(self):
        """Send current signal states to dashboard"""
        if not self.connected or not self.socket:
            return
        
        try:
            signals = self.simulation.get_signal_states()
            signal_data = {
                'signals': {
                    '0': signals[NORTH],    # North
                    '1': signals[EAST],     # East  
                    '2': signals[SOUTH],    # South
                    '3': signals[WEST]      # West
                },
                'manual_mode': self.manual_mode,
                'timestamp': time.time()
            }
            
            self.socket.emit('signal_state_update', signal_data)
            
        except Exception as e:
            print(f"❌ Error broadcasting signal state: {e}")


class Vehicle:
    """Represents a vehicle in the simulation"""
    
    def __init__(self, vehicle_type, direction, lane, x, y, dx, dy):
        self.type = vehicle_type
        self.direction = direction
        self.lane = lane
        self.x = x
        self.y = y
        self.dx = dx  # direction vector x
        self.dy = dy  # direction vector y
        self.speed = VEHICLE_SPEEDS[vehicle_type]
        self.stopped = False
        self.crossed_intersection = False
        self.color = VEHICLE_COLORS[vehicle_type]
        
        # Load vehicle image
        self.load_image()
        
        # Calculate target positions for removal
        if direction == NORTH:
            self.remove_y = -50
        elif direction == SOUTH:
            self.remove_y = WINDOW_HEIGHT + 50
        elif direction == EAST:
            self.remove_x = WINDOW_WIDTH + 50
        elif direction == WEST:
            self.remove_x = -50
    
    def load_image(self):
        """Load vehicle image based on type and direction"""
        direction_folder = DIRECTION_IMAGE_NAMES[self.direction]
        image_path = asset_path(direction_folder, f"{self.type}.png")
        
        try:
            self.original_image = pygame.image.load(image_path)
            self.current_image = self.original_image.copy()
            # Get dimensions from actual image
            self.width = self.current_image.get_width()
            self.height = self.current_image.get_height()
        except Exception as e:
            print(f"⚠️ Could not load image {image_path}: {e}")
            # Fallback to colored rectangle
            self.original_image = None
            self.current_image = None
            self.width = 15 if self.type == "bike" else 20
            self.height = 10 if self.type == "bike" else 15
    
    def update(self, signal_state, vehicles_ahead):
        """Update vehicle position based on traffic signals and other vehicles"""
        # Check if vehicle should be removed
        if self.should_remove():
            return False
        
        # Check if vehicle should stop at red light
        should_stop = self.should_stop_at_signal(signal_state)
        
        # Check for vehicles ahead
        should_stop_for_vehicle = self.should_stop_for_vehicle(vehicles_ahead)
        
        if should_stop or should_stop_for_vehicle:
            self.stopped = True
        else:
            self.stopped = False
            # Move vehicle
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed
        
        return True
    
    def should_stop_at_signal(self, signal_state):
        """Check if vehicle should stop at traffic signal"""
        if self.crossed_intersection or signal_state == SIGNAL_GREEN:
            return False
        
        # Check distance to stop line
        if self.direction == NORTH:
            return self.y > STOP_LINES[NORTH] and not self.crossed_intersection
        elif self.direction == SOUTH:
            return self.y < STOP_LINES[SOUTH] and not self.crossed_intersection
        elif self.direction == EAST:
            return self.x > STOP_LINES[EAST] and not self.crossed_intersection
        elif self.direction == WEST:
            return self.x < STOP_LINES[WEST] and not self.crossed_intersection
        
        return False
    
    def should_stop_for_vehicle(self, vehicles_ahead):
        """Check if vehicle should stop for vehicle ahead"""
        if not vehicles_ahead:
            return False
        
        min_distance = 30  # Minimum following distance
        
        for other in vehicles_ahead:
            if other.lane == self.lane and other.direction == self.direction:
                # Calculate distance based on direction
                if self.direction == NORTH:
                    distance = other.y - (self.y - self.height)
                elif self.direction == SOUTH:
                    distance = (self.y + self.height) - other.y
                elif self.direction == EAST:
                    distance = (self.x + self.width) - other.x
                elif self.direction == WEST:
                    distance = other.x - (self.x - self.width)
                else:
                    continue
                
                if 0 < distance < min_distance:
                    return True
        
        return False
    
    def should_remove(self):
        """Check if vehicle should be removed from simulation"""
        if self.direction == NORTH:
            return self.y < self.remove_y
        elif self.direction == SOUTH:
            return self.y > self.remove_y
        elif self.direction == EAST:
            return self.x > self.remove_x
        elif self.direction == WEST:
            return self.x < self.remove_x
        
        return False
    
    def check_intersection_crossing(self):
        """Check if vehicle has crossed the intersection"""
        if not self.crossed_intersection:
            # Simple intersection boundary check
            in_intersection_x = (INTERSECTION_CENTER_X - INTERSECTION_SIZE//2 < self.x < 
                               INTERSECTION_CENTER_X + INTERSECTION_SIZE//2)
            in_intersection_y = (INTERSECTION_CENTER_Y - INTERSECTION_SIZE//2 < self.y < 
                               INTERSECTION_CENTER_Y + INTERSECTION_SIZE//2)
            
            if in_intersection_x and in_intersection_y:
                self.crossed_intersection = True
    
    def draw(self, screen):
        """Draw vehicle on screen"""
        if self.current_image and self.original_image:
            # Draw vehicle image
            if self.stopped:
                # Create a darker version when stopped
                darkened = self.original_image.copy()
                darkened.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
                screen.blit(darkened, (self.x - self.width//2, self.y - self.height//2))
            else:
                screen.blit(self.current_image, (self.x - self.width//2, self.y - self.height//2))
        else:
            # Fallback to colored rectangle
            color = self.color if not self.stopped else tuple(c // 2 for c in self.color)
            pygame.draw.rect(screen, color, (self.x - self.width//2, self.y - self.height//2, 
                                           self.width, self.height))
            
            # Draw direction indicator for fallback
            if self.direction == NORTH:
                pygame.draw.polygon(screen, WHITE, [
                    (self.x, self.y - self.height//2),
                    (self.x - 3, self.y),
                    (self.x + 3, self.y)
                ])
            elif self.direction == SOUTH:
                pygame.draw.polygon(screen, WHITE, [
                    (self.x, self.y + self.height//2),
                    (self.x - 3, self.y),
                    (self.x + 3, self.y)
                ])
            elif self.direction == EAST:
                pygame.draw.polygon(screen, WHITE, [
                    (self.x + self.width//2, self.y),
                    (self.x, self.y - 3),
                    (self.x, self.y + 3)
                ])
            elif self.direction == WEST:
                pygame.draw.polygon(screen, WHITE, [
                    (self.x - self.width//2, self.y),
                    (self.x, self.y - 3),
                    (self.x, self.y + 3)
                ])


class TrafficSignal:
    """Represents a traffic signal for one direction"""
    
    def __init__(self, direction):
        self.direction = direction
        self.state = SIGNAL_RED
        self.last_change = time.time()
        self.signal_images = self.load_signal_images()
    
    def load_signal_images(self):
        """Load signal images"""
        images = {}
        signal_types = [SIGNAL_RED, SIGNAL_YELLOW, SIGNAL_GREEN]
        
        for signal_type in signal_types:
            try:
                image_path = asset_path(f"signals/{signal_type}.png")
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    # Scale signal images to appropriate size
                    images[signal_type] = pygame.transform.scale(image, (30, 90))
                    print(f"✅ Loaded signal image: {signal_type}")
                else:
                    print(f"⚠️ Signal image not found: {image_path}")
            except Exception as e:
                print(f"❌ Error loading signal image {signal_type}: {e}")
        
        return images
    
    def set_state(self, new_state):
        """Set signal state"""
        if new_state in [SIGNAL_RED, SIGNAL_YELLOW, SIGNAL_GREEN]:
            if self.state != new_state:
                print(f"🚦 Signal {DIRECTION_NAMES[self.direction]}: {self.state} -> {new_state}")
                self.state = new_state
                self.last_change = time.time()
    
    def get_signal_position(self):
        """Get position for drawing signal"""
        if self.direction == NORTH:
            return (INTERSECTION_CENTER_X - 60, INTERSECTION_CENTER_Y + 80)
        elif self.direction == SOUTH:
            return (INTERSECTION_CENTER_X + 60, INTERSECTION_CENTER_Y - 80)
        elif self.direction == EAST:
            return (INTERSECTION_CENTER_X - 80, INTERSECTION_CENTER_Y - 60)
        elif self.direction == WEST:
            return (INTERSECTION_CENTER_X + 80, INTERSECTION_CENTER_Y + 60)
    
    def draw(self, screen):
        """Draw traffic signal"""
        x, y = self.get_signal_position()
        
        # Try to use signal image first
        if self.state in self.signal_images:
            signal_img = self.signal_images[self.state]
            img_rect = signal_img.get_rect(center=(x, y))
            screen.blit(signal_img, img_rect)
        else:
            # Fallback to colored circles
            # Signal box
            pygame.draw.rect(screen, BLACK, (x-15, y-45, 30, 90))
            pygame.draw.rect(screen, WHITE, (x-13, y-43, 26, 86))
            
            # Signal lights
            colors = [DARK_GRAY, DARK_GRAY, DARK_GRAY]
            if self.state == SIGNAL_RED:
                colors[0] = RED
            elif self.state == SIGNAL_YELLOW:
                colors[1] = YELLOW
            elif self.state == SIGNAL_GREEN:
                colors[2] = GREEN
            
            pygame.draw.circle(screen, colors[0], (x, y-25), 8)  # Red
            pygame.draw.circle(screen, colors[1], (x, y), 8)     # Yellow
            pygame.draw.circle(screen, colors[2], (x, y+25), 8)  # Green
        
        # Direction label
        font = pygame.font.Font(None, 24)
        text = font.render(DIRECTION_NAMES[self.direction], True, BLACK)
        text_rect = text.get_rect(center=(x, y-60))
        screen.blit(text, text_rect)


class ManualSimulation:
    """Main manual traffic simulation class"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Manual Traffic Simulation - Dashboard Controlled")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Load intersection background image
        self.load_background()
        
        # Initialize traffic signals
        self.signals = {
            NORTH: TrafficSignal(NORTH),
            EAST: TrafficSignal(EAST),
            SOUTH: TrafficSignal(SOUTH),
            WEST: TrafficSignal(WEST)
        }
        
        # Vehicle management
        self.vehicles = []
        self.spawn_timer = 0
        self.spawn_interval = 120  # frames between spawns
        
        # Statistics
        self.vehicles_spawned = 0
        self.vehicles_completed = 0
        
        # Initialize manual control client
        self.control_client = ManualControlClient(self)
        
        # Running state
        self.running = True
    
    def load_background(self):
        """Load intersection background image"""
        try:
            bg_path = asset_path("intersection.png")
            self.background_image = pygame.image.load(bg_path)
            # Scale to fit window if needed
            if (self.background_image.get_width() != WINDOW_WIDTH or 
                self.background_image.get_height() != WINDOW_HEIGHT):
                self.background_image = pygame.transform.scale(
                    self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
            print("✅ Loaded intersection background image")
        except Exception as e:
            print(f"⚠️ Could not load intersection background: {e}")
            self.background_image = None
    
    def set_signal_state(self, direction, state):
        """Set state for a specific traffic signal"""
        if direction in self.signals:
            self.signals[direction].set_state(state)
    
    def get_signal_states(self):
        """Get current states of all signals"""
        return {direction: signal.state for direction, signal in self.signals.items()}
    
    def spawn_vehicle(self):
        """Spawn a new vehicle from a random direction"""
        direction = random.choice([NORTH, EAST, SOUTH, WEST])
        vehicle_type = random.choice(VEHICLE_TYPES)
        lane = random.randint(0, 1)  # Choose lane 0 or 1
        
        # Get spawn position for this direction and lane
        lane_info = LANE_POSITIONS[direction][lane]
        x, y, dx, dy = lane_info
        
        # Adjust spawn position to be off-screen
        if direction == NORTH:
            y = WINDOW_HEIGHT + 50
        elif direction == SOUTH:
            y = -50
        elif direction == EAST:
            x = -50
        elif direction == WEST:
            x = WINDOW_WIDTH + 50
        
        vehicle = Vehicle(vehicle_type, direction, lane, x, y, dx, dy)
        self.vehicles.append(vehicle)
        self.vehicles_spawned += 1
    
    def update_vehicles(self):
        """Update all vehicles"""
        vehicles_to_remove = []
        
        for i, vehicle in enumerate(self.vehicles):
            # Get signal state for this vehicle's direction
            signal_state = self.signals[vehicle.direction].state
            
            # Get vehicles ahead in the same direction and lane
            vehicles_ahead = [v for v in self.vehicles[:i] if 
                            v.direction == vehicle.direction and v.lane == vehicle.lane]
            
            # Update vehicle
            if not vehicle.update(signal_state, vehicles_ahead):
                vehicles_to_remove.append(vehicle)
                self.vehicles_completed += 1
            else:
                vehicle.check_intersection_crossing()
        
        # Remove completed vehicles
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Manual keyboard controls for testing
                if event.key == pygame.K_1:
                    self.cycle_signal(NORTH)
                elif event.key == pygame.K_2:
                    self.cycle_signal(EAST)
                elif event.key == pygame.K_3:
                    self.cycle_signal(SOUTH)
                elif event.key == pygame.K_4:
                    self.cycle_signal(WEST)
                elif event.key == pygame.K_SPACE:
                    self.spawn_vehicle()
    
    def cycle_signal(self, direction):
        """Cycle through signal states (for testing)"""
        current = self.signals[direction].state
        if current == SIGNAL_RED:
            self.set_signal_state(direction, SIGNAL_GREEN)
        elif current == SIGNAL_GREEN:
            self.set_signal_state(direction, SIGNAL_YELLOW)
        elif current == SIGNAL_YELLOW:
            self.set_signal_state(direction, SIGNAL_RED)
    
    def draw_intersection(self):
        """Draw the intersection"""
        if self.background_image:
            # Use the actual intersection image
            self.screen.blit(self.background_image, (0, 0))
        else:
            # Fallback to programmatic drawing
            # Road surface
            pygame.draw.rect(self.screen, DARK_GRAY, 
                            (0, INTERSECTION_CENTER_Y - 60, WINDOW_WIDTH, 120))
            pygame.draw.rect(self.screen, DARK_GRAY, 
                            (INTERSECTION_CENTER_X - 60, 0, 120, WINDOW_HEIGHT))
            
            # Lane markings
            for i in range(4):
                # Horizontal lanes
                y = INTERSECTION_CENTER_Y - 30 + i * 20
                for x in range(0, WINDOW_WIDTH, 40):
                    if not (INTERSECTION_CENTER_X - 60 < x < INTERSECTION_CENTER_X + 60):
                        pygame.draw.rect(self.screen, YELLOW, (x, y-1, 20, 2))
                
                # Vertical lanes  
                x = INTERSECTION_CENTER_X - 30 + i * 20
                for y in range(0, WINDOW_HEIGHT, 40):
                    if not (INTERSECTION_CENTER_Y - 60 < y < INTERSECTION_CENTER_Y + 60):
                        pygame.draw.rect(self.screen, YELLOW, (x-1, y, 2, 20))
            
            # Stop lines
            # North stop line
            pygame.draw.rect(self.screen, WHITE, 
                            (INTERSECTION_CENTER_X - 60, STOP_LINES[NORTH], 120, 3))
            # South stop line
            pygame.draw.rect(self.screen, WHITE, 
                            (INTERSECTION_CENTER_X - 60, STOP_LINES[SOUTH], 120, 3))
            # East stop line
            pygame.draw.rect(self.screen, WHITE, 
                            (STOP_LINES[EAST], INTERSECTION_CENTER_Y - 60, 3, 120))
            # West stop line
            pygame.draw.rect(self.screen, WHITE, 
                            (STOP_LINES[WEST], INTERSECTION_CENTER_Y - 60, 3, 120))
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Title
        title = self.font.render("Manual Traffic Simulation", True, BLACK)
        self.screen.blit(title, (20, 20))
        
        # Connection status
        status_color = GREEN if self.control_client.connected else RED
        status_text = "Connected" if self.control_client.connected else "Disconnected"
        status = self.font.render(f"Dashboard: {status_text}", True, status_color)
        self.screen.blit(status, (20, 60))
        
        # Manual mode status
        mode_color = GREEN if self.control_client.manual_mode else GRAY
        mode_text = "ON" if self.control_client.manual_mode else "OFF"
        mode = self.font.render(f"Manual Mode: {mode_text}", True, mode_color)
        self.screen.blit(mode, (20, 100))
        
        # Statistics
        stats = [
            f"Vehicles Spawned: {self.vehicles_spawned}",
            f"Vehicles Active: {len(self.vehicles)}",
            f"Vehicles Completed: {self.vehicles_completed}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font.render(stat, True, BLACK)
            self.screen.blit(stat_surface, (WINDOW_WIDTH - 300, 20 + i * 40))
        
        # Instructions
        instructions = [
            "Dashboard Manual Control:",
            "Use the Manual Control panel",
            "in the dashboard sidebar",
            "",
            "Keyboard (Testing):",
            "1-4: Cycle signals",
            "Space: Spawn vehicle"
        ]
        
        small_font = pygame.font.Font(None, 24)
        for i, instruction in enumerate(instructions):
            inst_surface = small_font.render(instruction, True, BLACK)
            self.screen.blit(inst_surface, (20, WINDOW_HEIGHT - 200 + i * 25))
    
    def run(self):
        """Main simulation loop"""
        print("🚦 Starting Manual Traffic Simulation")
        print("🎛️ Connect to dashboard at http://localhost:3001")
        print("📱 Use Manual Control panel to control traffic signals")
        
        while self.running:
            # Handle events
            self.handle_events()
            
            # Spawn vehicles periodically
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_vehicle()
                self.spawn_timer = 0
            
            # Update simulation
            self.update_vehicles()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_intersection()
            
            # Draw vehicles
            for vehicle in self.vehicles:
                vehicle.draw(self.screen)
            
            # Draw traffic signals
            for signal in self.signals.values():
                signal.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
            
            # Broadcast signal state periodically
            if self.spawn_timer % 60 == 0:  # Every second
                self.control_client.broadcast_signal_state()
        
        pygame.quit()
        if self.control_client.socket:
            self.control_client.socket.disconnect()


if __name__ == "__main__":
    simulation = ManualSimulation()
    try:
        simulation.run()
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        pygame.quit()
        sys.exit()