import torch
import cv2
import numpy as np
import os
import threading
import time
from datetime import datetime
import streamlit as st
from ultralytics import YOLO

# Configuration
CONF_THRESHOLD = 0.5
RECORD_DURATION = 5
BEEP_DURATION = 1000  # milliseconds
BEEP_FREQUENCY = 440  # Hz

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

class SurveillanceSystem:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.recording = False
        self.frames = []
        self.record_start_time = 0
        self.latest_frame = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.last_beep_time = 0
        self.BEEP_COOLDOWN = 2  # seconds
        
        if not self.cap.isOpened():
            st.error("Error: Could not open camera")
            st.stop()

    def play_beep(self):
        try:
            import winsound
            winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
        except:
            try:
                os.system('afplay /System/Library/Sounds/Ping.aiff & sleep 5')
            except:
                os.system('beep -f %s -l %s' % (BEEP_FREQUENCY, BEEP_DURATION))

    def detect_people(self, frame):
        results = model(frame)
        detections = results[0].boxes.data.cpu().numpy()
        # st.text(f"Detections: {detections}")
        people_detected = [d for d in detections if int(d[5]) == 0]  # Class 0 is 'person' in COCO dataset
        
        if people_detected:
            st.text("Yes, INTRUDERS detected")
            for det in people_detected:
                xmin, ymin, xmax, ymax, conf, cls = det
                frame = cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                frame = cv2.putText(frame, f"Person {conf:.2f}", (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Add "INTRUDER DETECTED" in big bold letters
            frame = cv2.putText(frame, "INTRUDER DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
            
            # Display current system time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.text(f"Current System Time: {current_time}")
            
            # # Check if current time is between 6pm and 4am
            # current_hour = datetime.now().hour
            # if current_hour >= 18 or current_hour < 4:
            #     st.text("INTRUDER DETECTION is ON")
            
            if time.time() - self.last_beep_time > self.BEEP_COOLDOWN:
                self.play_beep()
                self.last_beep_time = time.time()
            return True, frame
        return False, frame

    def save_recording(self):
        if not self.frames:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("recordings", exist_ok=True)
        filename = f"recordings/{timestamp}.mp4"
        
        frame_size = (self.frames[0].shape[1], self.frames[0].shape[0])
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(filename, fourcc, 20.0, frame_size)
        
        for frame in self.frames:
            out.write(frame)
        out.release()
        
        st.session_state.last_recording = filename
        st.rerun()

    def processing_loop(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            with self.lock:
                self.latest_frame = frame.copy()

            if self.recording:
                self.frames.append(frame)
                if time.time() - self.record_start_time >= RECORD_DURATION:
                    self.recording = False
                    self.save_recording()
                    self.frames = []
            else:
                detected_people, frame = self.detect_people(frame)
                if detected_people:
                    self.latest_frame = frame
                    self.recording = True
                    self.record_start_time = time.time()
                    st.session_state.alert = True
                    st.rerun()

    def stop(self):
        self.stop_event.set()
        self.cap.release()

# Streamlit UI
st.title("AI Surveillance System")
st.markdown("Monitoring for human presence...")

if "alert" not in st.session_state:
    st.session_state.alert = False
if "last_recording" not in st.session_state:
    st.session_state.last_recording = None

if "system" not in st.session_state:
    st.session_state.system = SurveillanceSystem()
    processing_thread = threading.Thread(target=st.session_state.system.processing_loop)
    processing_thread.daemon = True
    processing_thread.start()

# Display current system time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.text(f"Current System Time: {current_time}")

# Check if current time is between 6pm and 4am
current_hour = datetime.now().hour
if current_hour >= 18 or current_hour < 4:
    st.text("Evening time, intruder detection is on!")
    st.markdown('<span style="color:red">INTRUDER DETECTION is ON</span>', unsafe_allow_html=True)
    if st.session_state.system.recording is True:
        st.markdown('<span style="color:red">INTRUDER is detected, recording...</span>', unsafe_allow_html=True)
placeholder = st.empty()

while True:
    if st.session_state.system.latest_frame is not None:
        with st.session_state.system.lock:
            frame = st.session_state.system.latest_frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        placeholder.image(frame, channels="RGB", use_column_width=True)
    
    if st.session_state.alert:
        st.warning("Person detected! Recording started...")
        st.session_state.alert = False
    
    if st.session_state.last_recording:
        st.success(f"Last recording saved at: {st.session_state.last_recording}")
        st.session_state.last_recording = None
    
    time.sleep(0.1)
