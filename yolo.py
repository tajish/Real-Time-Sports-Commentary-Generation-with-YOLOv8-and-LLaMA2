import math
import cv2
import os
import pandas as pd
import torch.nn as nn
from ultralytics import YOLO
from LlamaExpert import generate_commentary


def detectfootballs(tmp_path):
    video_path = tmp_path
    temp_video_path = 'static/videos/newd.mp4'
    model = YOLO("Models/best.pt")

    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    time_per_frame = 1 / fps
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (frame_width, frame_height))

    previous_center = None
    pixel_to_meter = 0.05
    speeds = []
    frame_count = 0
    window_size = 30
    commentary_log = []

    last_commentary = ""
    commentary_frames = 0
    display_duration = fps * 2  

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        results = model(frame, conf=0.3)

        for result in results[0].boxes.data:
            x1, y1, x2, y2 = map(int, result[:4].tolist())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            if previous_center:
                prev_x, prev_y = previous_center
                distance_pixels = math.sqrt((center_x - prev_x) ** 2 + (center_y - prev_y) ** 2)
                distance_meters = distance_pixels * pixel_to_meter
                speed = (distance_meters / time_per_frame) * 3.6
            else:
                speed = 0
            speeds.append(speed)
            previous_center = (center_x, center_y)

            radius = max((x2 - x1) // 2, (y2 - y1) // 2)
            cv2.circle(frame, (center_x, center_y), radius, (0, 0, 255), 1)
            cv2.putText(frame, f"Speed: {speed:.2f} km/h", (center_x, center_y - radius - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        if frame_count % window_size == 0:
            start = frame_count - window_size
            end = frame_count
            speed_window = speeds[start:end]
            commentary_text = generate_commentary(speed_window, start, end)

            if not isinstance(commentary_text, str):
                try:
                    commentary_text = commentary_text.content
                except AttributeError:
                    commentary_text = str(commentary_text)

            last_commentary = commentary_text
            commentary_frames = display_duration  

        
        if commentary_frames > 0 and last_commentary:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            (text_width, text_height), baseline = cv2.getTextSize(str(last_commentary), font, font_scale, thickness)
            x = (frame_width - text_width) // 2
            y = frame_height - 30
            offset = 70  

            overlay = frame.copy()
            cv2.rectangle(frame,
                        (x - 10, y - text_height - 10 - offset),
                        (x + text_width + 10, y + baseline + 10 - offset),
                        (0, 0, 0), -1)
            
            alpha = 0.4  
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            cv2.putText(frame, last_commentary, (x, y - offset),
                        font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

            commentary_frames -= 1  

        out.write(frame)

        
    cap.release()
    out.release()
    cv2.destroyAllWindows()