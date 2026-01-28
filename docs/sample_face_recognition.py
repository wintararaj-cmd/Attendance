# Face Recognition Logic (Python/FastAPI)

This module handles the core logic for:
1.  **Preprocessing**: Face detection and alignment.
2.  **Embedding**: Generating 128-d or 512-d vectors.
3.  **Matching**: Cosine similarity check.
4.  **Liveness**: Blink detection or texture analysis (simplified example).

## Dependencies
`pip install fastapi uvicorn opencv-python deepface numpy`

## Code Structure

```python
import cv2
import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine

# Configuration
THRESHOLD = 0.40  # Similarity threshold (lower calculation for cosine usually, DeepFace handles this internally too)
MODEL_NAME = "Facenet512" # High accuracy model

class FaceRecognitionService:
    def __init__(self):
        # Initialize any models if needed to keep in memory
        pass

    def verify_liveness(self, frame) -> bool:
        """
        Simple liveness detection using eye aspect ratio or texture analysis.
        For production, use a dedicated liveness SDK or Deep Learning model.
        Here we simulate a basic check (e.g., checking for pixel variance/noise to avoid printed photos).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Placeholder: Check for sufficient frequency variance (blur check)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < 100: # Image is too blurry (potential screen spoof)
            return False
        return True

    def register_face(self, image_path: str) -> list:
        """
        Generate embedding for a registration image.
        """
        try:
            embedding = DeepFace.represent(img_path=image_path, model_name=MODEL_NAME)[0]["embedding"]
            return embedding
        except Exception as e:
            print(f"Error registering face: {e}")
            return None

    def recognize_face(self, live_image_path: str, stored_embeddings: list):
        """
        Compare live image against stored embeddings.
        """
        try:
            # 1. Generate embedding for live image
            live_objs = DeepFace.represent(img_path=live_image_path, model_name=MODEL_NAME, enforce_detection=False)
            if not live_objs:
                return {"status": "failed", "reason": "No face detected"}
            
            live_embedding = live_objs[0]["embedding"]

            # 2. Compare with stored embeddings
            # In production, use Vector DB (Pinecone/Milvus/pgvector) for speed
            best_score = 1.0 # 1.0 is max distance (no match), 0.0 is perfect match
            match_found = False

            for stored_emb in stored_embeddings:
                score = cosine(live_embedding, stored_emb)
                if score < THRESHOLD:
                    best_score = score
                    match_found = True
                    break
            
            if match_found:
                return {"status": "success", "confidence": 1 - best_score}
            else:
                return {"status": "failed", "reason": "No match found", "score": best_score}

        except Exception as e:
            return {"status": "error", "message": str(e)}

# API Integration Example
from fastapi import FastAPI, UploadFile, File

app = FastAPI()
face_service = FaceRecognitionService()

# Mock Database
mock_db_embeddings = [] 

@app.post("/register/")
async def register(file: UploadFile = File(...)):
    # Save temp file
    with open("temp_reg.jpg", "wb") as f:
        f.write(await file.read())
    
    embedding = face_service.register_face("temp_reg.jpg")
    if embedding:
        mock_db_embeddings.append(embedding)
        return {"message": "Face registered successfully"}
    return {"error": "Could not register face"}

@app.post("/attendance/")
async def mark_attendance(file: UploadFile = File(...)):
    # Save temp file
    with open("temp_live.jpg", "wb") as f:
        f.write(await file.read())
        
    # Check Liveness first
    frame = cv2.imread("temp_live.jpg")
    if not face_service.verify_liveness(frame):
        return {"result": "failed", "reason": "Liveness check failed"}

    # Match
    result = face_service.recognize_face("temp_live.jpg", mock_db_embeddings)
    return result
```
