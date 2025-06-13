"""
AutoZoom - TV Monitor Detection and Optimal Zoom Finder

This script automatically finds the optimal zoom level for a camera pointed at a TV/monitor.
It works by:
1. Connecting to an IP camera with zoom control capability
2. Starting from minimum zoom (1%)
3. Gradually increasing zoom level while detecting the TV using YOLOv8
4. Stopping when the TV either:
   - Covers more than the specified threshold of the frame area (default 90%)
   - Touches the edges of the frame
5. Saving the best frame (highest zoom while keeping the TV fully in view)
6. Setting the camera to the optimal zoom level

Requirements:
- IP camera with HTTP control interface
- YOLOv8 model (uses yolov8n.pt by default)
- OpenCV, requests, ultralytics packages

Usage:
- Configure the IP address and other parameters in the CONFIG section
- Run the script: python autozoom.py
"""
import cv2
import requests
import time
from ultralytics import YOLO
from tqdm import tqdm

# --- CONFIG ---
ip = "192.168.1.109"
stream_url = f"http://{ip}:8080/video"
zoom_url = f"http://{ip}:8080/ptz?zoom={{}}"
target_class = 62  # COCO: tvmonitor
wait_after_zoom = 1.0  # seconds
save_path = "tv_max_zoom.jpg"
area_threshold = 0.9  # 90% of frame area

# --- Load model ---
model = YOLO("yolov8n.pt")

# --- Reset zoom ---
print("🔄 Resetting to zoom level 1")
requests.get(zoom_url.format(1))
time.sleep(wait_after_zoom)

# --- Search for max safe zoom ---
best_frame = None
best_zoom = 2

for zoom in tqdm(range(1, 101), desc="Zoom sweep"):
    # Apply zoom
    requests.get(zoom_url.format(zoom))
    time.sleep(wait_after_zoom)

    # Grab frame
    cap = cv2.VideoCapture(stream_url)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Frame grab failed")
        break

    img_h, img_w = frame.shape[:2]
    frame_area = img_h * img_w

    # Detect TV
    results = model(frame, verbose=False)
    found_tv = False

    for r in results:
        for b in r.boxes:
            if int(b.cls[0]) == target_class:
                x1, y1, x2, y2 = map(int, b.xyxy[0])
                box_area = (x2 - x1) * (y2 - y1)

                # Area threshold check
                if box_area > frame_area * area_threshold:
                    print(f"📏 TV covers >{area_threshold*100:.0f}% of frame at zoom {zoom} → stopping")
                    found_tv = False
                    break

                # Frame boundary check
                if x1 <= 1 or y1 <= 1 or x2 >= img_w - 2 or y2 >= img_h - 2:
                    print(f"🚫 TV touches frame edge at zoom {zoom} → stopping")
                    found_tv = False
                    break

                # TV is valid
                found_tv = True
                best_frame = frame.copy()
                best_zoom = zoom
                break
        if not found_tv:
            break

    if not found_tv:
        break

# --- Finalize ---
if best_frame is not None:
    cv2.imwrite(save_path, best_frame)
    print(f"✅ Saved best frame at zoom {best_zoom}% → {save_path}")
else:
    print("❌ No valid zoom level found — check visibility or lighting")

# Optional: set camera back to best zoom
requests.get(zoom_url.format(best_zoom))
