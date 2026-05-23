import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import subprocess


def process_video(input_path: str, output_path: str, job: dict) -> dict:
    model = YOLO("models/salamander.pt")

    cap = cv2.VideoCapture(input_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    trails = defaultdict(list)
    time_on_screen = defaultdict(int)
    heatmap = np.zeros((h, w), dtype=np.float32)
    frame_id_log = []

    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # update shared progress state
        job["progress"] = round(
            (frame_idx / max(total_frames, 1)) * 100,
            1
        )

        results = model.track(frame, persist=True, verbose=False)

        frame_ids = []

        if results[0].boxes is not None:
            boxes = results[0].boxes

            for box in boxes:
                if box.id is None:
                    continue

                tid = int(box.id)

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                conf = float(box.conf[0])

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 100),
                    2
                )

                cv2.putText(
                    frame,
                    f"ID {tid} {conf:.2f}",
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 100),
                    2
                )

                trails[tid].append((cx, cy))

                time_on_screen[tid] += 1

                heatmap[
                    max(0, cy - 15):cy + 15,
                    max(0, cx - 15):cx + 15
                ] += 1

                pts = np.array(trails[tid][-40:], dtype=np.int32)

                if len(pts) > 1:
                    cv2.polylines(
                        frame,
                        [pts],
                        False,
                        (255, 165, 0),
                        2
                    )

                frame_ids.append(tid)

        frame_id_log.append(frame_ids)

        out.write(frame)

        frame_idx += 1

    cap.release()
    out.release()

    distances = {}

    for tid, pts in trails.items():
        d = sum(
            np.linalg.norm(
                np.array(pts[i]) - np.array(pts[i - 1])
            )
            for i in range(1, len(pts))
        )

        distances[str(tid)] = round(d, 2)

    time_on_screen = {
        k: v for k, v in time_on_screen.items()
        if v >= 3
    }

    distances = {
        k: v for k, v in distances.items()
        if int(k) in time_on_screen
    }

    valid_ids = set(time_on_screen.keys())

    detection_counts = [
        sum(1 for tid in frame_ids if tid in valid_ids)
        for frame_ids in frame_id_log
    ]

    browser_path = output_path.replace(".mp4", "_web.mp4")

    subprocess.run([
        "ffmpeg",
        "-i",
        output_path,
        "-vcodec",
        "libx264",
        "-acodec",
        "aac",
        browser_path
    ], check=True)

    return {
        "fps": fps,
        "total_frames": frame_idx,
        "detection_counts": detection_counts,
        "time_on_screen": {
            str(k): v for k, v in time_on_screen.items()
        },
        "total_distance_px": distances,
    }