
# FaceCrop

FaceCrop is a Command Line Interface (CLI) tool that allows you to resize multiple images or a single image to a specified square size. The tool uses face detection to center the face in the resized image, ensuring that the primary subject of the photo is the focal point.

## Features
- Bulk resize images in a directory or a single image.
- Centers on the detected face or the center of the image if no face is detected.
- Allows custom output directory and size specification.
- Provides warning messages if no face is detected.

## Installation

### Dependencies
- Python 3.x
- OpenCV (`opencv-python`)
- dlib
- Pillow (`PIL`)

Install the dependencies using:

```bash
pip install opencv-python dlib Pillow
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
- `--dir`: Path to the directory containing images.
- `--file`: Path to a single image file.
- `--output`: (Optional) Path to the output directory.
- `--size`: (Optional) Size of the output square image (default 224).

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
