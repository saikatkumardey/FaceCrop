# FaceCrop

[![PyPI version](https://badge.fury.io/py/facecrop.svg)](https://pypi.org/project/facecrop/)
[![Python](https://img.shields.io/pypi/pyversions/facecrop.svg)](https://pypi.org/project/facecrop/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FaceCrop** is a powerful CLI tool for intelligent, face-centered image resizing. Using dlib's face detection, it automatically crops and resizes images to ensure faces remain the focal point—perfect for profile pictures, thumbnails, and batch image processing.

## ✨ Features

- 🎯 **Face-centered cropping** - Automatic face detection with dlib
- ⚡ **Fast batch processing** - Multiprocessing support for high throughput
- 📊 **Progress tracking** - Real-time progress bars and structured logging
- 🔄 **Smart fallback** - Center crop when no face detected
- 🎨 **Format support** - JPG, PNG, BMP, WebP, TIFF
- 🚀 **Production-ready** - Robust error handling and validation

## 📦 Installation

### From PyPI (recommended)

```bash
pip install facecrop
```

### From source with uv

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/saikatkumardey/FaceCrop.git
cd FaceCrop
uv pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

```bash
# Process a single image
facecrop image.jpg

# Process entire directory
facecrop photos/

# Custom output size and location
facecrop photos/ --size 512 --output results/

# Use specific number of CPU cores
facecrop photos/ --workers 8
```

## 📖 Usage

### Basic Commands

```bash
# Single image (outputs to ./output/)
facecrop portrait.jpg

# Directory processing
facecrop my_photos/

# Custom output directory
facecrop photos/ -o processed/

# Custom size (64-4096 pixels)
facecrop photos/ -s 384

# Control parallelism
facecrop photos/ -w 4
```

### Advanced Examples

```bash
# High-resolution output for printing
facecrop headshots/ --size 2048 --output prints/

# Quick preview processing (single core)
facecrop samples/ --size 128 --workers 1

# Batch process with custom output
facecrop team_photos/ -s 512 -o website/avatars/ -w 16
```

### Python API

```python
from facecrop import resize_and_center_face, process_images

# Process single image
image = resize_and_center_face("photo.jpg", size=224)
if image:
    image.save("output.jpg")

# Batch processing
successful, failed = process_images(
    "photos/",
    size=512,
    output_folder="processed/",
    workers=4
)
print(f"Processed: {successful}, Failed: {failed}")
```

## ⚙️ Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `input` | - | Path to image or directory | *required* |
| `--output` | `-o` | Output directory | `./output` |
| `--size` | `-s` | Output size in pixels (square) | `224` |
| `--workers` | `-w` | Number of CPU cores to use | auto |
| `--version` | `-v` | Show version | - |
| `--quiet` | `-q` | Suppress progress output | `false` |

## 🏗️ How It Works

1. **Face Detection**: Uses dlib's HOG-based detector to locate faces
2. **Smart Cropping**: Centers crop on the first detected face
3. **Fallback**: If no face found, crops from image center
4. **Resizing**: Scales to exact square dimensions
5. **Output**: Saves as `{filename}.out{extension}`

## 📋 Requirements

- Python 3.8+
- OpenCV (cv2)
- dlib
- Pillow
- tqdm
- loguru

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=facecrop --cov-report=html

# Run tests in parallel
pytest -n auto
```

## 🤝 Contributing

Contributions are welcome! Please check out our [Contributing Guide](CONTRIBUTING.md).

```bash
# Quick setup with Make (uses uv - super fast!)
git clone https://github.com/saikatkumardey/FaceCrop.git
cd FaceCrop
make dev

# Or manual setup
uv venv && uv pip install -e ".[dev]"

# Run tests (10-100x faster than pip!)
make test          # Current Python version
make test-all      # All Python 3.8-3.12 versions

# Code quality
make lint          # Run all linters
make format        # Auto-format code

# Build package
make build
```

## 📝 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.

## 🙏 Acknowledgments

- Built with [dlib](http://dlib.net/) for face detection
- Inspired by the need for better profile picture cropping

## 📮 Support

- 🐛 [Report bugs](https://github.com/saikatkumardey/FaceCrop/issues)
- 💡 [Request features](https://github.com/saikatkumardey/FaceCrop/issues)
- ⭐ Star this repo if you find it useful!
