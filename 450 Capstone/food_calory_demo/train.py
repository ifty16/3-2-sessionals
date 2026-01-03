print("TRAIN SCRIPT STARTED")

from ultralytics import YOLO

print("Ultralytics imported")

model = YOLO("yolov8n-seg.pt")
print("Model loaded")

model.train(
    data="dataset/data.yaml",
    epochs=1,
    imgsz=640,
    batch=4,
    name="food_seg_demo"
)
