# Zoom in and capture bounding boxes of a TV monitor using YOLOv8; store images with
# bounding boxes at different zoom levels.


import cv2
import requests
from ultralytics import YOLO
import time
import os

# --- CONFIG ---
ip           = "192.168.1.109"
stream_url   = f"http://{ip}:8080/video"
zoom_url     = f"http://{ip}:8080/ptz?zoom={{}}"
target_class = 62       # COCO class ID for 'tvmonitor'
zooms        = list(range(0, 101, 1))  # change step as desired
output_dir   = "captures"

# --- Prepare output directory ---
os.makedirs(output_dir, exist_ok=True)

# --- Load model once ---
model = YOLO("yolov8n.pt")

# --- Helper to apply zoom and grab one frame ---
def grab_frame(zoom_pct):
    # set zoom
    requests.get(zoom_url.format(zoom_pct))
    time.sleep(0.8)  # give camera time to settle
    cap = cv2.VideoCapture(stream_url)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError(f"Failed to grab frame at zoom {zoom_pct}")
    return frame

# --- Main loop ---
for z in zooms:
    try:
        frame = grab_frame(z)
    except RuntimeError as e:
        print(e)
        continue

    # run detection
    results = model(frame)

    # find first matching box
    box = None
    for r in results:
        for b in r.boxes:
            if int(b.cls[0]) == target_class:
                box = b.xyxy[0].cpu().numpy().astype(int)
                break
        if box is not None:
            break

    # annotate
    if box is not None:
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, f"Zoom {z}%", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
    else:
        cv2.putText(frame, f"Zoom {z}% - no TV detected", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)

    # save to file
    filename = os.path.join(output_dir, f"bb_{z}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Saved {filename}")

# --- Reset zoom to 0 at end ---
requests.get(zoom_url.format(0))
print("Done. All images saved in:", output_dir)
