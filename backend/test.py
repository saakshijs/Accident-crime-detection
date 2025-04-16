import pathlib
import torch
from pathlib import Path
pathlib.PosixPath = pathlib.WindowsPath

# Ensure the path is correct
yolov5_dir = r'C:\Users\saakshi\AI-Object-Detection\backend\yolov5'
model_path = yolov5_dir + r'\runs\train\accident_model\weights\best.pt'

# Load model correctly
model = torch.hub.load(
    yolov5_dir,  # Path to YOLOv5 repo
    'custom', 
    path=model_path, 
    source='local', 
    force_reload=True  # Force reload to avoid caching issues
)
