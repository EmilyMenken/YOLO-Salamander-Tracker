from ultralytics import YOLO

model = YOLO("backend/models/salamander.pt")
results = model.predict("dataset/raw_videos/video.mp4", save=True)