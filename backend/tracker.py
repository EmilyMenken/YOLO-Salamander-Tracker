import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import subprocess


model = YOLO("models/salamander.pt")

def process_video(input_path: str, output_path: str, progress: dict) -> dict:
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    trails = defaultdict(list)
    time_on_screen = defaultdict(int)
    heatmap = np.zeros((h, w), dtype=np.float32)
    detection_counts = []

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        progress["progress"] = round((frame_idx / max(total_frames, 1)) * 100, 1)

        results = model.track(frame, persist=True, verbose=False)
        count = 0

        if results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                if box.id is None:
                    continue
                tid = int(box.id)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                conf = float(box.conf[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 100), 2)
                cv2.putText(frame, f"ID {tid} {conf:.2f}", (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 100), 2)

                trails[tid].append((cx, cy))
                time_on_screen[tid] += 1
                heatmap[max(0, cy-15):cy+15, max(0, cx-15):cx+15] += 1

                pts = np.array(trails[tid][-40:], dtype=np.int32)
                if len(pts) > 1:
                    cv2.polylines(frame, [pts], False, (255, 165, 0), 2)

                count += 1

        detection_counts.append(count)
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    distances = {}
    for tid, pts in trails.items():
        d = sum(np.linalg.norm(np.array(pts[i]) - np.array(pts[i-1]))
                for i in range(1, len(pts)))
        distances[str(tid)] = round(d, 2)

    browser_path = output_path.replace(".mp4", "_web.mp4")
    subprocess.run([
        "ffmpeg", "-i", output_path, "-vcodec", "libx264", "-acodec", "aac", browser_path
    ], check=True)    

    return {
        "fps": fps,
        "total_frames": frame_idx,
        "detection_counts": detection_counts,
        "time_on_screen": {str(k): v for k, v in time_on_screen.items()},
        "total_distance_px": distances,
    }