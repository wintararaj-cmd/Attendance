from deepface import DeepFace
import cv2
import numpy as np

# Create a dummy image
img = np.zeros((500, 500, 3), dtype="uint8")
cv2.rectangle(img, (100, 100), (300, 300), (255, 255, 255), -1) # Draw a white square face-ish thing
cv2.imwrite("test_face.jpg", img)

try:
    print("Testing DeepFace...")
    # This won't detect a face in a white square probably, but it will test if the function RUNS
    # We enforce_detection=False to just test the pipeline
    embedding = DeepFace.represent(img_path="test_face.jpg", model_name="VGG-Face", enforce_detection=False)
    print("DeepFace Success!")
except Exception as e:
    print(f"DeepFace Failed: {e}")
