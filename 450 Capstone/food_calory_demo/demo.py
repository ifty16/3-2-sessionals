from ultralytics import YOLO
import cv2

# load trained segmentation model
model = YOLO("runs/segment/food_seg_demo3/weights/best.pt")

#print class names
print("Class names:", model.names)

# image to test
img_path = "D:/academics/buet cse undergrad/3-2/3-2 sessionals/450 Capstone/food_calory_demo/test.jpg"   # put any food image here

# inference
print("Running inference...")
results = model(img_path, conf = 0.1)

# draw masks + boxes
annotated = results[0].plot()

# show window
cv2.imshow("Food Segmentation Demo", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()


