import cv2
import os

VIDEO_PATH = "../../dataset/raw_videos/salamanderWalkingInWoods.mp4"
OUTPUT_DIR = "../../dataset/extracted_frames"

FRAME_SKIP = 15  # Save every 15th frame

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

frame_count = 0
saved_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    if frame_count % FRAME_SKIP == 0:
        filename = f"frame_{saved_count:04d}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)

        cv2.imwrite(filepath, frame)

        print(f"Saved {filename}")

        saved_count += 1

    frame_count += 1

cap.release()

print(f"\nFinished. Extracted {saved_count} frames.")