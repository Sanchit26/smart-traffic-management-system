# LAG
# NO. OF VEHICLES IN SIGNAL CLASS
# stops not used
# DISTRIBUTION
# BUS TOUCHING ON TURNS
# Distribution using python class

# *** IMAGE XY COOD IS TOP LEFT
import random
import math
import time
import threading
import json  # NEW: for structured event logs
# from vehicle_detection import detection
import pygame
import sys
import os
import tempfile  # NEW: for temporary frame files

try:
    import requests  # NEW: for posting frames/events to backend
except Exception:
    requests = None

try:
    import socketio  # NEW: for real-time manual control from dashboard
except Exception:
    socketio = None

# options={
#    'model':'./cfg/yolo.cfg',     #specifying the path of model
#    'load':'./bin/yolov2.weights',   #weights
#    'threshold':0.3     #minimum confidence factor to create a box, greater than 0.3 good
# }

# tfnet=TFNet(options)    #READ ABOUT TFNET

# Default values of signal times
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
simTime = 100  # change this to change time of simulation
timeElapsed = 0

currentGreen = 0  # Indicates which signal is green
nextGreen = (currentGreen + 1) % noOfSignals
currentYellow = 0  # Indicates whether yellow signal is on or off

# Average times for vehicles to pass the intersection
carTime = 2
bikeTime = 1
rickshawTime = 2.25
busTime = 2.5
truckTime = 2.5

# Count of cars at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2

# Red signal time at which cars will be detected at a signal
detectionTime = 5

# === NEW: Extend speeds with ambulance (emergency vehicle) ===
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'rickshaw': 2, 'bike': 2.5,
          'ambulance': 3.0}  # average speeds of vehicles

# Coordinates of start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike', 5: 'ambulance'}  # NEW: ambulance
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]
vehicleCountTexts = ["0", "0", "0", "0"]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580, 580, 580], 'down': [320, 320, 320], 'left': [810, 810, 810], 'up': [545, 545, 545]}

mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 'left': {'x': 695, 'y': 425},
       'up': {'x': 695, 'y': 400}}
rotationAngle = 3

# Gap between vehicles
gap = 15  # stopping gap
gap2 = 15  # moving gap

pygame.init()
simulation = pygame.sprite.Group()

# Base dir for assets so relative loads work regardless of current working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(*parts):
    return os.path.join(SCRIPT_DIR, *parts)


# === NEW: Simple structured event logger for future dashboard integration ===
class EventLogger:
    events = []  # store events in-memory for optional future use

    @staticmethod
    def log(event_type, data=None):
        evt = {
            "ts": time.time(),
            "event": event_type,
        }
        if data:
            evt.update(data)
        EventLogger.events.append(evt)
        # Print out a structured log that a dashboard can consume later
        print(json.dumps(evt))
        # NEW: Try to POST event to backend /events endpoint
        EVENTS_URL = os.environ.get("EVENTS_URL", "http://localhost:5050/simulation/events")
        if requests is not None:
            try:
                resp = requests.post(
                    EVENTS_URL,
                    json=evt,
                    timeout=0.5,
                )
                if resp.status_code != 200:
                    raise Exception("Non-200 response")
            except Exception:
                # Fallback: write event to local file for later pickup
                try:
                    tmp_path = os.path.join(tempfile.gettempdir(), "sim_events.jsonl")
                    with open(tmp_path, "a") as f:
                        f.write(json.dumps(evt) + "\n")
                except Exception:
                    pass


# === NEW: Emergency preemption state ===
emergency_active = False
emergency_direction = None  # one of 'right','down','left','up'
last_signal_change_from = None  # track for logging transitions

# === NEW: Manual control system ===
manual_mode_active = False
manual_control_socket = None

class ManualControlSystem:
    def __init__(self):
        self.socket_client = None
        self.connected = False
        self.manual_mode = False
        self.initialize_connection()
    
    def initialize_connection(self):
        """Initialize Socket.IO connection to dashboard backend for manual control"""
        if socketio is None:
            print("⚠️ socketio not available, manual control disabled")
            return
        
        try:
            self.socket_client = socketio.Client()
            
            # Set up event handlers
            self.socket_client.on('connect', self.on_connect)
            self.socket_client.on('disconnect', self.on_disconnect)
            self.socket_client.on('simulation_manual_signal', self.on_manual_signal)
            self.socket_client.on('simulation_manual_mode', self.on_manual_mode_toggle)
            
            self.socket_client.connect('http://localhost:5050', transports=['polling'])
            
        except Exception as e:
            print(f"⚠️ Failed to connect manual control: {e}")
            self.connected = False
    
    def on_connect(self):
        print("🎛️ Manual control system connected to dashboard")
        self.connected = True
    
    def on_disconnect(self):
        print("🎛️ Manual control system disconnected")
        self.connected = False
    
    def on_manual_signal(self, data):
        """Handle manual signal change from dashboard"""
        global signals, currentGreen, currentYellow, nextGreen, manual_mode_active
        
        if not self.manual_mode:
            print("⚠️ Manual signal command received but manual mode not active")
            return
        
        try:
            signal_id = data['signal_id']  # e.g., 'signal_1'
            new_state = data['new_state']  # 'red', 'yellow', 'green'
            
            # Extract signal index (0-3) from signal_id
            signal_index = int(signal_id.split('_')[1]) - 1
            
            if 0 <= signal_index < len(signals):
                # Apply manual signal change
                if new_state == 'green':
                    # Set this signal to green, others to red
                    currentGreen = signal_index
                    currentYellow = 0
                    nextGreen = (currentGreen + 1) % noOfSignals
                    
                    for i in range(noOfSignals):
                        if i == signal_index:
                            signals[i].green = 30  # 30 seconds green
                            signals[i].yellow = 0
                            signals[i].red = 0
                        else:
                            signals[i].green = 0
                            signals[i].yellow = 0
                            signals[i].red = 30  # 30 seconds red
                    
                    EventLogger.log("manual_signal_change", {
                        "signal": signal_index + 1,
                        "state": "green",
                        "direction": directionNumbers[signal_index]
                    })
                    
                elif new_state == 'yellow':
                    # Set current signal to yellow
                    if signal_index == currentGreen:
                        currentYellow = 1
                        signals[signal_index].green = 0
                        signals[signal_index].yellow = 5
                        signals[signal_index].red = 0
                    
                    EventLogger.log("manual_signal_change", {
                        "signal": signal_index + 1,
                        "state": "yellow",
                        "direction": directionNumbers[signal_index]
                    })
                    
                elif new_state == 'red':
                    # Set signal to red
                    signals[signal_index].green = 0
                    signals[signal_index].yellow = 0
                    signals[signal_index].red = 60  # 60 seconds red
                    
                    # If this was the green signal, stop it
                    if signal_index == currentGreen:
                        currentYellow = 0
                        # Find next available signal or set all red
                        found_green = False
                        for i in range(noOfSignals):
                            if signals[i].green > 0:
                                currentGreen = i
                                found_green = True
                                break
                        if not found_green:
                            currentGreen = -1  # All red state
                    
                    EventLogger.log("manual_signal_change", {
                        "signal": signal_index + 1,
                        "state": "red",
                        "direction": directionNumbers[signal_index]
                    })
                
                print(f"🎛️ Manual signal {signal_index + 1} set to {new_state}")
                
        except Exception as e:
            print(f"❌ Error processing manual signal command: {e}")
    
    def on_manual_mode_toggle(self, data):
        """Handle manual mode toggle from dashboard"""
        global manual_mode_active
        
        try:
            self.manual_mode = data['manual_mode']
            manual_mode_active = self.manual_mode
            
            if self.manual_mode:
                print("🎛️ MANUAL MODE ACTIVATED - Dashboard control enabled")
                EventLogger.log("manual_mode_activated", {"timestamp": time.time()})
            else:
                print("🎛️ MANUAL MODE DEACTIVATED - Returning to automatic control")
                EventLogger.log("manual_mode_deactivated", {"timestamp": time.time()})
                
        except Exception as e:
            print(f"❌ Error processing manual mode toggle: {e}")
    
    def send_signal_states(self):
        """Send current signal states to dashboard"""
        if not self.connected or self.socket_client is None:
            return
        
        try:
            signal_data = {
                'signals': {
                    'signal_1': {
                        'direction': 'North',
                        'state': self.get_signal_state(0),
                        'timer': self.get_signal_timer(0)
                    },
                    'signal_2': {
                        'direction': 'East', 
                        'state': self.get_signal_state(1),
                        'timer': self.get_signal_timer(1)
                    },
                    'signal_3': {
                        'direction': 'South',
                        'state': self.get_signal_state(2),
                        'timer': self.get_signal_timer(2)
                    },
                    'signal_4': {
                        'direction': 'West',
                        'state': self.get_signal_state(3),
                        'timer': self.get_signal_timer(3)
                    }
                },
                'manual_mode': self.manual_mode,
                'timestamp': time.time()
            }
            
            self.socket_client.emit('signal_state_update', signal_data)
            
        except Exception as e:
            print(f"❌ Error sending signal states: {e}")
    
    def get_signal_state(self, signal_index):
        """Get current state of a signal"""
        global currentGreen, currentYellow
        
        if signal_index == currentGreen:
            if currentYellow == 1:
                return 'yellow'
            else:
                return 'green'
        else:
            return 'red'
    
    def get_signal_timer(self, signal_index):
        """Get remaining time for current signal state"""
        if signal_index < len(signals):
            signal = signals[signal_index]
            if signal.green > 0:
                return signal.green
            elif signal.yellow > 0:
                return signal.yellow
            elif signal.red > 0:
                return signal.red
        return 0

# Initialize manual control system
manual_control = ManualControlSystem()


class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        # NEW (Anomaly detection): track last movement time/pos
        self.last_pos = (self.x, self.y)
        self.last_moved_time = time.time()
        self.anomaly_reported = False
        vehicles[direction][lane].append(self)
        # self.stop = stops[direction][lane]
        self.index = len(vehicles[direction][lane]) - 1
        path = asset_path("images", direction, vehicleClass + ".png")
        # NEW: load with fallback to avoid breaking simulation if ambulance asset missing
        try:
            self.originalImage = pygame.image.load(path)
            self.currentImage = pygame.image.load(path)
        except Exception as e:
            fallback = asset_path("images", direction, "car.png")
            try:
                self.originalImage = pygame.image.load(fallback)
                self.currentImage = pygame.image.load(fallback)
                EventLogger.log("asset_missing", {"path": path, "fallback": fallback})
            except Exception:
                raise e

        if (direction == 'right'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][
                self.index - 1].crossed == 0):  # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().width - gap  # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            else:
                self.stop = defaultStop[direction]
            # Set new starting and stopping coordinate
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif (direction == 'left'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif (direction == 'down'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif (direction == 'up'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        # === NEW (Anomaly detection): detect if vehicle is stopped too long while having green ===
        def update_movement_tracking():
            moved = (self.x, self.y) != self.last_pos
            if moved:
                self.last_pos = (self.x, self.y)
                self.last_moved_time = time.time()
            return moved

        if (self.direction == 'right'):
            if (self.crossed == 0 and self.x + self.currentImage.get_rect().width > stopLines[
                self.direction]):  # if the image has crossed stop line now
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.x + self.currentImage.get_rect().width < mid[self.direction]['x']):
                    if ((self.x + self.currentImage.get_rect().width <= self.stop or (
                            currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                            self.index == 0 or self.x + self.currentImage.get_rect().width < (
                            vehicles[self.direction][self.lane][self.index - 1].x - gap2) or
                            vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                        self.x += self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if (self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.image = pygame.image.load(path)
                    else:
                        if (self.index == 0 or self.y + self.currentImage.get_rect().height < (
                                vehicles[self.direction][self.lane][
                                    self.index - 1].y - gap2) or self.x + self.currentImage.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - gap2)):
                            self.y += self.speed
            else:
                if ((self.x + self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or (
                        currentGreen == 0 and currentYellow == 0)) and (
                        self.index == 0 or self.x + self.currentImage.get_rect().width < (
                        vehicles[self.direction][self.lane][self.index - 1].x - gap2) or (
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x += self.speed  # move the vehicle



        elif (self.direction == 'down'):
            if (self.crossed == 0 and self.y + self.currentImage.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.y + self.currentImage.get_rect().height < mid[self.direction]['y']):
                    if ((self.y + self.currentImage.get_rect().height <= self.stop or (
                            currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                            self.index == 0 or self.y + self.currentImage.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - gap2) or
                            vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                        self.y += self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if (self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                         vehicles[self.direction][self.lane][
                                                             self.index - 1].currentImage.get_rect().width + gap2) or self.y < (
                                vehicles[self.direction][self.lane][self.index - 1].y - gap2)):
                            self.x -= self.speed
            else:
                if ((self.y + self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or (
                        currentGreen == 1 and currentYellow == 0)) and (
                        self.index == 0 or self.y + self.currentImage.get_rect().height < (
                        vehicles[self.direction][self.lane][self.index - 1].y - gap2) or (
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1))):
                    self.y += self.speed

        elif (self.direction == 'left'):
            if (self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.x > mid[self.direction]['x']):
                    if ((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                            self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                        self.index - 1].currentImage.get_rect().width + gap2) or vehicles[self.direction][self.lane][
                                self.index - 1].turned == 1)):
                        self.x -= self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if (self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.currentImage = pygame.image.load(path)
                    else:
                        if (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                         vehicles[self.direction][self.lane][
                                                             self.index - 1].currentImage.get_rect().height + gap2) or self.x > (
                                vehicles[self.direction][self.lane][self.index - 1].x + gap2)):
                            self.y -= self.speed
            else:
                if ((self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and (
                        self.index == 0 or self.x > (
                        vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                    self.index - 1].currentImage.get_rect().width + gap2) or (
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x -= self.speed  # move the vehicle
            # if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2))):
            #     self.x -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.y > mid[self.direction]['y']):
                    if ((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                            self.index == 0 or self.y > (
                            vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                        self.index - 1].currentImage.get_rect().height + gap2) or vehicles[self.direction][self.lane][
                                self.index - 1].turned == 1)):
                        self.y -= self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if (self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if (self.index == 0 or self.x < (vehicles[self.direction][self.lane][self.index - 1].x -
                                                         vehicles[self.direction][self.lane][
                                                             self.index - 1].currentImage.get_rect().width - gap2) or self.y > (
                                vehicles[self.direction][self.lane][self.index - 1].y + gap2)):
                            self.x += self.speed
            else:
                if ((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and (
                        self.index == 0 or self.y > (
                        vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                    self.index - 1].currentImage.get_rect().height + gap2) or (
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1))):
                    self.y -= self.speed

        # NEW (Anomaly detection): after attempting to move, update movement tracking and check stop duration
        moved_now = update_movement_tracking()
        # Only check anomaly for leading vehicle in lane, with green signal, not crossed
        if (
                self.index == 0 and self.crossed == 0 and currentYellow == 0 and directionNumbers[
            currentGreen] == self.direction
        ):
            stopped_for = time.time() - self.last_moved_time
            if stopped_for >= 20 and not self.anomaly_reported:
                self.anomaly_reported = True
                EventLogger.log(
                    "anomaly_detected",
                    {
                        "direction": self.direction,
                        "lane": self.lane,
                        "vehicleClass": self.vehicleClass,
                        "stopped_for_secs": round(stopped_for, 1),
                    },
                )


# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)
    repeat()


# Set time according to formula
def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime
    # Optional text-to-speech notification (macOS only). Safe no-op elsewhere.
    try:
        if sys.platform == "darwin":
            os.system("say detecting vehicles, " + directionNumbers[(currentGreen + 1) % noOfSignals])
    except Exception:
        pass
    #    detection_result=detection(currentGreen,tfnet)
    #    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (noOfBuses*busTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
    #    if(greenTime<defaultMinimum):
    #       greenTime = defaultMinimum
    #    elif(greenTime>defaultMaximum):
    #       greenTime = defaultMaximum
    # greenTime = len(vehicles[currentGreen][0])+len(vehicles[currentGreen][1])+len(vehicles[currentGreen][2])
    # noOfVehicles = len(vehicles[directionNumbers[nextGreen]][1])+len(vehicles[directionNumbers[nextGreen]][2])-vehicles[directionNumbers[nextGreen]]['crossed']
    # print("no. of vehicles = ",noOfVehicles)
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
    for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
        vehicle = vehicles[directionNumbers[nextGreen]][0][j]
        if (vehicle.crossed == 0):
            vclass = vehicle.vehicleClass
            # print(vclass)
            noOfBikes += 1
    for i in range(1, 3):
        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
            vehicle = vehicles[directionNumbers[nextGreen]][i][j]
            if (vehicle.crossed == 0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if (vclass == 'car'):
                    noOfCars += 1
                elif (vclass == 'bus'):
                    noOfBuses += 1
                elif (vclass == 'truck'):
                    noOfTrucks += 1
                elif (vclass == 'rickshaw'):
                    noOfRickshaws += 1
    # print(noOfCars)
    greenTime = math.ceil(((noOfCars * carTime) + (noOfRickshaws * rickshawTime) + (noOfBuses * busTime) + (
                noOfTrucks * truckTime) + (noOfBikes * bikeTime)) / (noOfLanes + 1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
    print('Green Time: ', greenTime)
    if (greenTime < defaultMinimum):
        greenTime = defaultMinimum
    elif (greenTime > defaultMaximum):
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[(currentGreen + 1) % (noOfSignals)].green = greenTime


# === NEW: Emergency detection utility ===
def check_and_update_emergency_state():
    global emergency_active, emergency_direction
    found_dir = None
    for d in ['right', 'down', 'left', 'up']:
        # If any ambulance is waiting (not crossed) in any lane of this direction
        waiting = any(
            (v.vehicleClass == 'ambulance' and v.crossed == 0)
            for lane in [0, 1, 2]
            for v in vehicles[d][lane]
        )
        if waiting:
            found_dir = d
            break

    if found_dir and not emergency_active:
        emergency_active = True
        emergency_direction = found_dir
        EventLogger.log("ambulance_detected", {"direction": found_dir})
    elif not found_dir and emergency_active:
        EventLogger.log("emergency_cleared", {"previous_direction": emergency_direction})
        emergency_active = False
        emergency_direction = None


def repeat():
    global currentGreen, currentYellow, nextGreen
    while (signals[currentGreen].green > 0):  # while the timer of current green signal is not zero
        printStatus()
        updateValues()
        # NEW: Emergency preemption — force early end of current green to switch immediately
        if emergency_active and directionNumbers[currentGreen] != emergency_direction:
            # Immediately end current green (skip yellow later)
            signals[currentGreen].green = 0
            signals[currentGreen].yellow = 0
            break
        if (signals[(currentGreen + 1) % (noOfSignals)].red == detectionTime):  # set time of next green signal
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)
    # If emergency is active, skip yellow and switch immediately
    if emergency_active:
        currentYellow = 0
    else:
        currentYellow = 1  # set yellow signal on
    vehicleCountTexts[currentGreen] = "0"
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    if not emergency_active:
        while (signals[currentGreen].yellow > 0):  # while the timer of current yellow signal is not zero
            printStatus()
            updateValues()
            time.sleep(1)
    currentYellow = 0  # set yellow signal off

    # reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    prev_dir_idx = currentGreen
    if emergency_active and emergency_direction is not None:
        # NEW: emergency preemption — switch to the emergency direction immediately
        currentGreen = [k for k, v in directionNumbers.items() if v == emergency_direction][0]
        # CHANGE: Do NOT force 60s; treat ambulance as normal for timing.
        # Keep existing configured green; if it's non-positive, give a minimal safety window.
        if signals[currentGreen].green <= 0:
            signals[currentGreen].green = defaultMinimum
        reason = "emergency_preemption"
    else:
        currentGreen = nextGreen  # set next signal as green signal
        reason = "normal_cycle"
    nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow + signals[
        currentGreen].green  # set the red time of next to next signal as (yellow time + green time) of next signal

    # NEW: structured log for signal change
    EventLogger.log(
        "signal_changed",
        {
            "from": directionNumbers[prev_dir_idx],
            "to": directionNumbers[currentGreen],
            "reason": reason,
        },
    )
    repeat()


# Print the signal timers on cmd
def printStatus():
    for i in range(0, noOfSignals):
        if (i == currentGreen):
            if (currentYellow == 0):
                print(" GREEN TS", i + 1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
            else:
                print("YELLOW TS", i + 1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
        else:
            print("   RED TS", i + 1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
    print()


# Update values of the signal timers after every second
def updateValues():
    global manual_mode_active
    
    # Skip automatic updates if in manual mode
    if manual_mode_active:
        return
    
    for i in range(0, noOfSignals):
        if (i == currentGreen):
            if (currentYellow == 0):
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# Generating vehicles in the simulation
def generateVehicles():
    while (True):
        # NEW: Occasionally spawn an ambulance with low probability
        if random.random() < 0.01:
            vehicle_type = 5  # ambulance
        else:
            vehicle_type = random.randint(0, 4)
        if (vehicle_type == 4):
            lane_number = 0
        else:
            lane_number = random.randint(0, 1) + 1
        will_turn = 0
        if (lane_number == 2):
            temp = random.randint(0, 4)
            if (temp <= 2):
                will_turn = 1
            elif (temp > 2):
                will_turn = 0
        temp = random.randint(0, 999)
        direction_number = 0
        a = [400, 800, 900, 1000]
        if (temp < a[0]):
            direction_number = 0
        elif (temp < a[1]):
            direction_number = 1
        elif (temp < a[2]):
            direction_number = 2
        elif (temp < a[3]):
            direction_number = 3
        v = Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],
                    will_turn)
        # NEW: On ambulance spawn, activate emergency and force immediate preemption
        if vehicle_type == 5:
            # Mark emergency state and force current green to end ASAP
            global emergency_active, emergency_direction
            emergency_active = True
            emergency_direction = directionNumbers[direction_number]
            EventLogger.log("ambulance_detected", {"direction": emergency_direction, "lane": lane_number})
            signals[currentGreen].green = 0
        time.sleep(0.75)


def simulationTime():
    global timeElapsed, simTime
    while (True):
        timeElapsed += 1
        time.sleep(1)
        if (timeElapsed == simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane', i + 1, ':', vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ', totalVehicles)
            print('Total time passed: ', timeElapsed)
            print('No. of vehicles passed per unit time: ', (float(totalVehicles) / float(timeElapsed)))
            os._exit(1)


class Main:
    thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=())
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread2.daemon = True
    thread2.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load(asset_path('images', 'mod_int.png'))

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load(asset_path('images', 'signals', 'red.png'))
    yellowSignal = pygame.image.load(asset_path('images', 'signals', 'yellow.png'))
    greenSignal = pygame.image.load(asset_path('images', 'signals', 'green.png'))
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread3.daemon = True
    thread3.start()

    # Frame streaming config (optional)
    POST_FRAMES = os.environ.get("POST_FRAMES", "0") == "1"
    FRAMES_URL = os.environ.get("FRAMES_URL", "http://localhost:5000/simulation/frame")
    FRAME_POST_INTERVAL = float(os.environ.get("FRAME_POST_INTERVAL", "0.5"))  # seconds
    last_frame_post = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))  # display background in simulation
        # NEW: Check and update emergency state based on current vehicles
        check_and_update_emergency_state()
        for i in range(0,
                       noOfSignals):  # display signal and set timer according to current status: green, yello, or red
            if (i == currentGreen):
                if (currentYellow == 1):
                    if (signals[i].yellow == 0):
                        signals[i].signalText = "STOP"
                    else:
                        signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    if (signals[i].green == 0):
                        signals[i].signalText = "SLOW"
                    else:
                        signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if (signals[i].red <= 10):
                    if (signals[i].red == 0):
                        signals[i].signalText = "GO"
                    else:
                        signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        # display signal timer and vehicle count
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, (1100, 50))

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            # vehicle.render(screen)
            vehicle.move()
        
        # Broadcast current signal states
        if manual_control and manual_control.socket_client and manual_control.socket_client.connected:
            try:
                # Extract just the current state string from each TrafficSignal object
                current_signals = {
                    'signals': {
                        '0': signals[0].current if hasattr(signals[0], 'current') else 'red',  # North
                        '1': signals[1].current if hasattr(signals[1], 'current') else 'red',  # East
                        '2': signals[2].current if hasattr(signals[2], 'current') else 'red',  # South
                        '3': signals[3].current if hasattr(signals[3], 'current') else 'red'   # West
                    },
                    'manual_mode': manual_control.manual_mode
                }
                manual_control.socket_client.emit('signal_state_update', current_signals)
            except Exception as e:
                print(f"Error broadcasting signal state: {e}")
        
        pygame.display.update()

        # NEW: Optionally post current frame to Dashboard backend, fallback to /tmp/sim_frame.png
        if POST_FRAMES:
            now_ts = time.time()
            if now_ts - last_frame_post >= FRAME_POST_INTERVAL:
                tmp_path = os.path.join(tempfile.gettempdir(), "sim_frame.png")
                try:
                    pygame.image.save(screen, tmp_path)
                    if requests is not None:
                        with open(tmp_path, "rb") as f:
                            data = f.read()
                        try:
                            resp = requests.post(
                                FRAMES_URL,
                                data=data,
                                headers={"Content-Type": "application/octet-stream"},
                                timeout=0.5,
                            )
                            if resp.status_code != 200:
                                raise Exception("Non-200 response")
                        except Exception:
                            # Fallback: frame is already saved to tmp_path
                            pass
                except Exception:
                    pass
                finally:
                    last_frame_post = now_ts


Main()


