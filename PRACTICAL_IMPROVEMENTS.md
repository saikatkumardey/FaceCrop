# FaceCrop: Practical Improvements for Solo Engineer

**Focus**: CPU-only, low-cost, open-source solutions
**Target**: Fix obvious bugs and add basic scalability
**Timeline**: 1-2 weeks of part-time work

---

## Critical Issues (Fix These First)

### 1. **No Error Handling** 🚨 HIGH PRIORITY

**Problem**: Code will crash on invalid images or missing files

**Current Code** (main.py:13):
```python
image = cv2.imread(image_path)  # Returns None if file doesn't exist!
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # CRASH if image is None
```

**Fix**:
```python
def resize_and_center_face(image_path, size):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # ... rest of code
        return pil_image
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None
```

**Impact**: Prevents crashes, allows batch processing to continue on errors

---

### 2. **No Input Validation** 🚨 HIGH PRIORITY

**Problem**: Processes ANY file, including .txt, .pdf, system files

**Current Code** (main.py:38):
```python
# Gets ALL files - could try to process README.md!
image_paths = [os.path.join(input_path, f) for f in os.listdir(input_path)
               if os.path.isfile(os.path.join(input_path, f))]
```

**Fix**:
```python
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

def is_valid_image(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_FORMATS

# In bulk_resize():
if is_directory:
    all_files = [os.path.join(input_path, f) for f in os.listdir(input_path)]
    image_paths = [f for f in all_files if os.path.isfile(f) and is_valid_image(f)]
```

**Also Add**:
```python
def validate_input(args):
    # Check path exists
    path = args.dir or args.file
    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path}")

    # Check size is reasonable
    if args.size < 64 or args.size > 4096:
        raise ValueError(f"Size must be between 64 and 4096, got {args.size}")
```

**Impact**: Prevents wasted processing, better error messages

---

### 3. **No Progress Indicator** 🟡 MEDIUM PRIORITY

**Problem**: User has no idea how long bulk processing will take

**Fix** (add tqdm):
```python
# Install: pip install tqdm
from tqdm import tqdm

for image_path in tqdm(image_paths, desc="Processing images"):
    resized_image = resize_and_center_face(image_path, size)
    # ... rest of code
```

**Impact**: Better UX, can estimate completion time

---

### 4. **No Parallel Processing** 🟡 MEDIUM PRIORITY

**Problem**: Processes one image at a time, wastes CPU cores

**Fix** (use multiprocessing):
```python
from multiprocessing import Pool, cpu_count
from functools import partial

def process_single_image(args):
    """Wrapper for multiprocessing"""
    image_path, size, output_folder = args
    try:
        resized_image = resize_and_center_face(image_path, size)
        if resized_image is None:
            return None

        name, extension = os.path.splitext(os.path.basename(image_path))
        output_name = name + ".out" + extension
        output_path = os.path.join(output_folder, output_name)
        resized_image.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error: {e}")
        return None

def bulk_resize(input_path, size, output_folder, is_directory=True, workers=None):
    # ... existing path setup code ...

    if workers is None:
        workers = cpu_count()  # Use all CPU cores

    # Prepare arguments for parallel processing
    args_list = [(path, size, output_folder) for path in image_paths]

    with Pool(workers) as pool:
        results = list(tqdm(
            pool.imap(process_single_image, args_list),
            total=len(args_list),
            desc="Processing images"
        ))

    successful = [r for r in results if r is not None]
    print(f"Processed {len(successful)}/{len(image_paths)} images")
```

**Impact**: 4-8x faster on multi-core machines (almost free performance!)

---

### 5. **No requirements.txt** 🟢 LOW PRIORITY (but easy)

**Problem**: Users don't know exact versions needed

**Fix** (create requirements.txt):
```
opencv-python>=4.8.0
dlib>=19.24.0
Pillow>=10.0.0
tqdm>=4.66.0
```

**Install**:
```bash
pip install -r requirements.txt
```

**Impact**: Easier setup, reproducible environments

---

### 6. **No Logging** 🟢 LOW PRIORITY

**Problem**: Print statements mixed with output, no log files

**Fix**:
```python
import logging

# Setup at top of main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('facecrop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Replace print() with logger.info(), logger.error(), etc.
logger.info(f"Found {len(faces)} faces in {image_path}")
logger.warning("No faces found, using center crop")
logger.error(f"Failed to process {image_path}: {e}")
```

**Impact**: Better debugging, log files for troubleshooting

---

### 7. **No Configuration File** 🟢 LOW PRIORITY

**Problem**: All settings hardcoded or CLI arguments

**Fix** (create config.yaml):
```yaml
# config.yaml
defaults:
  output_size: 224
  output_suffix: ".out"
  workers: 4  # CPU cores to use

processing:
  max_image_size_mb: 50
  supported_formats: [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

face_detection:
  min_face_size: 20  # pixels
  upsampling: 1  # dlib parameter
```

**Load in code**:
```python
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()
```

**Impact**: Easier to customize without changing code

---

## Optional Additions (For Basic Web Access)

### 8. **Simple Flask API** (Weekend Project)

**Why**: Let others use it via web interface

**Basic Implementation**:
```python
# api.py
from flask import Flask, request, send_file, jsonify
import os
from main import resize_and_center_face
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'

@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    size = int(request.form.get('size', 224))

    # Save uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # Process
    try:
        result = resize_and_center_face(input_path, size)
        output_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
        result.save(output_path)

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
```

**Run**:
```bash
pip install flask
python api.py
```

**Test**:
```bash
curl -X POST -F "file=@test.jpg" -F "size=224" http://localhost:5000/process -o output.jpg
```

---

### 9. **Basic Docker Container** (1-2 hours)

**Why**: Easy deployment, reproducible environment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies for dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port for API
EXPOSE 5000

# Default command
CMD ["python", "main.py", "--help"]
```

**Build & Run**:
```bash
# Build
docker build -t facecrop:latest .

# Run CLI
docker run -v $(pwd)/images:/data facecrop python main.py --dir /data

# Run API
docker run -p 5000:5000 facecrop python api.py
```

**docker-compose.yml** (for easy deployment):
```yaml
version: '3.8'
services:
  facecrop:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./images:/app/images
      - ./output:/app/output
    environment:
      - WORKERS=4
    command: python api.py
```

---

### 10. **Basic Tests** (2-3 hours)

**Why**: Catch bugs before they reach users

**tests/test_main.py**:
```python
import pytest
import os
from main import resize_and_center_face, is_valid_image
from PIL import Image

def test_valid_image_formats():
    assert is_valid_image("test.jpg") == True
    assert is_valid_image("test.png") == True
    assert is_valid_image("test.txt") == False
    assert is_valid_image("README.md") == False

def test_resize_with_face():
    # Use one of your example images
    result = resize_and_center_face("example/example-1.png", 224)
    assert result is not None
    assert result.size == (224, 224)

def test_resize_invalid_file():
    result = resize_and_center_face("nonexistent.jpg", 224)
    assert result is None  # Should handle error gracefully

def test_resize_small_size():
    result = resize_and_center_face("example/example-1.png", 64)
    assert result.size == (64, 64)
```

**Run**:
```bash
pip install pytest
pytest tests/
```

---

## Priority Roadmap

### Week 1: Critical Fixes
- [ ] Add error handling to resize_and_center_face() (1 hour)
- [ ] Add input validation (1 hour)
- [ ] Add progress indicator with tqdm (30 min)
- [ ] Create requirements.txt (15 min)
- [ ] Test with example images (30 min)

**Result**: Robust CLI tool that won't crash

### Week 2: Performance & Usability
- [ ] Add multiprocessing support (2-3 hours)
- [ ] Add logging (1 hour)
- [ ] Create config.yaml (1 hour)
- [ ] Write basic tests (2 hours)

**Result**: 4-8x faster, better logging

### Optional (Weekend): Web Access
- [ ] Build simple Flask API (3-4 hours)
- [ ] Create Dockerfile (1-2 hours)
- [ ] Test deployment (1 hour)

**Result**: Can serve via HTTP

---

## Performance Estimates (CPU-Only)

### Current (Single-threaded):
- ~200-500ms per image (dlib face detection)
- 100 images: ~30-50 seconds
- 1000 images: ~5-8 minutes

### With Multiprocessing (4 cores):
- ~50-125ms per image (parallel)
- 100 images: ~8-13 seconds
- 1000 images: ~1-2 minutes

### With Better Face Detector (MediaPipe - optional):
- ~50-100ms per image (faster CPU model)
- But requires additional dependency

---

## Cost Estimate (Low-Cost Hosting)

### Option 1: VPS (DigitalOcean, Linode)
- $12/month: 2 vCPU, 4GB RAM
- Can handle ~500-1000 images/day
- Install Docker, run Flask API

### Option 2: Serverless (Render, Railway)
- Free tier: 750 hours/month
- $7/month: Basic plan
- Good for low-moderate usage

### Option 3: Self-hosted (Raspberry Pi)
- $50 one-time (Pi 4, 4GB)
- Good for personal use
- ~100ms per image on Pi 4

**Recommendation**: Start with Option 2 (Render free tier), scale to Option 1 if needed

---

## Next Steps

1. **Fix critical issues** (Week 1 tasks)
2. **Test thoroughly** with your example images
3. **Add multiprocessing** for better performance
4. **(Optional) Build simple API** if you need web access
5. **Deploy to VPS** when ready

---

## Quick Wins (Do These Today!)

```bash
# 1. Add requirements.txt
cat > requirements.txt << EOF
opencv-python>=4.8.0
dlib>=19.24.0
Pillow>=10.0.0
tqdm>=4.66.0
EOF

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add .gitignore for Python (if not already)
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore

# 4. Run tests with example images
python main.py --dir example --output example/test_output
```

---

## Summary

**Critical fixes needed**:
1. ❌ Add error handling (prevents crashes)
2. ❌ Add input validation (prevents processing non-images)
3. ⚠️ Add progress indicator (better UX)
4. ⚠️ Add multiprocessing (4-8x speedup)
5. ✅ Add requirements.txt (easy setup)

**Total effort**: 1-2 weeks part-time
**Cost**: $0-$12/month (VPS if you deploy)
**Performance gain**: 4-8x with multiprocessing

**Bottom line**: Focus on fixes #1-2 first (prevent crashes), then #4 (big performance win). Everything else is nice-to-have.

---

**Last Updated**: 2026-01-05
**For**: Solo engineer, CPU-only, low-cost setup
