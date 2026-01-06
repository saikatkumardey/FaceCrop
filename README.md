
# FaceCrop

FaceCrop is a Command Line Interface (CLI) tool that allows you to resize multiple images or a single image to a specified square size. The tool uses face detection to center the face in the resized image, ensuring that the primary subject of the photo is the focal point.

## Features
- Bulk resize images in a directory or a single image
- Face-centered intelligent cropping with dlib
- Multiprocessing support for fast batch processing
- Progress indicators and structured logging
- Automatic fallback to center crop when no face detected

## Installation

### Using uv (recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .
```

### Using pip

```bash
pip install opencv-python dlib Pillow tqdm loguru
```

## Usage

### Resize Images in a Directory

If no output directory is specified, the resized images will be saved in a "output" directory inside the input directory.

```bash
python main.py --dir /path/to/image/directory --output /path/to/output/directory --size 224
```

### Resize a Single Image
```bash
python main.py --file /path/to/single/image.jpg --output /path/to/output/directory --size 224
```

### Options
- `--dir`: Path to the directory containing images
- `--file`: Path to a single image file
- `--output`: (Optional) Path to the output directory
- `--size`: (Optional) Size of the output square image (default: 224)
- `--workers`: (Optional) Number of worker processes (default: auto)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
