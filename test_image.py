from ultralytics import YOLO

model = YOLO("backend/models/salamander.pt")
results = model.predict("dataset/extracted_frames/frame_salamaderStuck_0007.jpg", save=True)
print(results[0].boxes)