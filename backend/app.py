# Import necessary libraries
from fastapi import FastAPI, File, UploadFile # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from starlette.responses import Response # type: ignore
import io
import torch
import numpy as np
import pathlib
from pathlib import Path
from PIL import Image
import time

# ✅ Import notify function (Email only)
from notify import notify_all  # Make sure notify_all sends only email

# Fix compatibility for Windows/Linux path handling
pathlib.PosixPath = pathlib.WindowsPath

# Initialize FastAPI app
app = FastAPI(
    title="YOLOv5 Object Detection API",
    description="Detect objects in images and return results in JSON or image format",
    version="1.0.0",
)

# Configure CORS
origins = ["http://localhost", "http://localhost:8000", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to YOLOv5 and models
yolov5_dir = Path(r"C:\Users\saakshi\AI-Object-Detection\backend\yolov5")
accident_model_path = yolov5_dir / "runs" / "train" / "accident_model" / "weights" / "best.pt"
theft_model_path = yolov5_dir / "runs" / "train" / "theft_detection_model" / "weights" / "best.pt"

# Load models
try:
    accident_model = torch.hub.load(
        yolov5_dir.as_posix(), "custom", path=accident_model_path.as_posix(),
        source="local", force_reload=True
    )
    theft_model = torch.hub.load(
        yolov5_dir.as_posix(), "custom", path=theft_model_path.as_posix(),
        source="local", force_reload=True
    )
    print("✅ Both models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    accident_model = None
    theft_model = None

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to YOLOv5 FastAPI!"}

# Health check
@app.get('/notify/v1/health')
def get_health():
    return {"msg": "OK"}

from fastapi import Form

@app.post("/object-to-json-realtime")
async def detect_objects_realtime(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = get_image_from_bytes(image_bytes)
    if image is None:
        return {"error": "Invalid image format"}

    try:
        results_accident = accident_model(image)
        results_thief = theft_model(image)

        accident_detected = len(results_accident.xyxy[0]) > 0
        thief_detected = len(results_thief.xyxy[0]) > 0

        accident_json = results_accident.pandas().xyxy[0].to_dict(orient="records")
        theft_json = results_thief.pandas().xyxy[0].to_dict(orient="records")

        return {
            "accident_detected": accident_detected,
            "thief_detected": thief_detected,
            "detections": accident_json + theft_json
        }
    except Exception as e:
        return {"error": f"Real-time detection failed: {str(e)}"}

# Convert bytes to image
def get_image_from_bytes(image_bytes):
    try:
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return None

# ✅ JSON Endpoint
@app.post("/object-to-json")
async def detect_objects_json(file: UploadFile = File(...)):
    if not accident_model or not theft_model:
        return {"error": "One or both models are not loaded."}

    image_bytes = await file.read()
    image = get_image_from_bytes(image_bytes)
    if image is None:
        return {"error": "Invalid image format"}

    try:
        t_start = time.time()
        results_accident = accident_model(image)
        t_mid = time.time()
        results_thief = theft_model(image)
        t_end = time.time()

        accident_detected = len(results_accident.xyxy[0]) > 0
        thief_detected = len(results_thief.xyxy[0]) > 0

        # Logging
        if accident_detected:
            results_accident.print()
        if thief_detected:
            results_thief.print()
        if not (accident_detected or thief_detected):
            print("No detections")

        accident_json = results_accident.pandas().xyxy[0].to_dict(orient="records")
        theft_json = results_thief.pandas().xyxy[0].to_dict(orient="records")
        combined = accident_json + theft_json

        # ✅ Email Notification
        if accident_detected or thief_detected:
            notify_all(accident=accident_detected, theft=thief_detected)

        return {
            "accident_detected": accident_detected,
            "thief_detected": thief_detected,
            "detection_summary": combined,
            "timing": {
                "accident_inference_ms": round((t_mid - t_start) * 1000, 2),
                "theft_inference_ms": round((t_end - t_mid) * 1000, 2),
                "total_inference_ms": round((t_end - t_start) * 1000, 2)
            }
        }
    except Exception as e:
        return {"error": f"Inference failed: {str(e)}"}

# ✅ Image Endpoint
@app.post("/object-to-img")
async def detect_objects_image(file: UploadFile = File(...)):
    if not accident_model or not theft_model:
        return {"error": "One or both models are not loaded."}

    image_bytes = await file.read()
    image = get_image_from_bytes(image_bytes)
    if image is None:
        return {"error": "Invalid image format"}

    try:
        results_accident = accident_model(image)
        results_thief = theft_model(image)

        accident_detected = len(results_accident.xyxy[0]) > 0
        thief_detected = len(results_thief.xyxy[0]) > 0

        if accident_detected:
            results_accident.print()
        if thief_detected:
            results_thief.print()
        if not (accident_detected or thief_detected):
            print("No detections")

        # ✅ Email Notification
        if accident_detected or thief_detected:
            notify_all(accident=accident_detected, theft=thief_detected)

        results_accident.render()
        results_thief.render()

        img_np = results_thief.imgs[0]
        img_pil = Image.fromarray(img_np)
        img_bytes = io.BytesIO()
        img_pil.save(img_bytes, format="JPEG")

        return Response(content=img_bytes.getvalue(), media_type="image/jpeg")
    except Exception as e:
        return {"error": f"Image processing failed: {str(e)}"}

# Run app
if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
