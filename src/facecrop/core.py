"""Core image processing functionality."""

from pathlib import Path
from multiprocessing import Pool, cpu_count
import dlib
import cv2
from PIL import Image
from tqdm import tqdm
from loguru import logger

detector = dlib.get_frontal_face_detector()
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}


def is_valid_image(path):
    """Check if file has a supported image extension."""
    return Path(path).suffix.lower() in SUPPORTED_FORMATS


def resize_and_center_face(image_path, size=224):
    """
    Resize image to square, centered on detected face.

    Args:
        image_path: Path to input image
        size: Output size in pixels (square)

    Returns:
        PIL Image if successful, None otherwise
    """
    try:
        if not Path(image_path).exists():
            logger.error(f"File not found: {image_path}")
            return None

        if not is_valid_image(image_path):
            logger.error(f"Unsupported format: {image_path}")
            return None

        image = cv2.imread(str(image_path))
        if image is None:
            logger.error(f"Could not read: {image_path}")
            return None

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = detector(image_rgb)

        if faces:
            logger.info(f"Found {len(faces)} face(s) in {Path(image_path).name}")
            face = faces[0]
            center_x = (face.left() + face.right()) // 2
            center_y = (face.top() + face.bottom()) // 2
        else:
            logger.warning(f"No faces in {Path(image_path).name}, using center crop")
            center_y, center_x = image.shape[0] // 2, image.shape[1] // 2

        left = max(center_x - size // 2, 0)
        top = max(center_y - size // 2, 0)
        right = min(center_x + size // 2, image.shape[1])
        bottom = min(center_y + size // 2, image.shape[0])

        cropped = image[top:bottom, left:right]
        if cropped.size == 0:
            logger.error(f"Empty crop: {image_path}")
            return None

        resized = cv2.resize(cropped, (size, size))
        return Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

    except Exception as e:
        logger.error(f"Error processing {image_path}: {e}")
        return None


def _process_single(args):
    """Process single image (multiprocessing wrapper)."""
    image_path, size, output_folder = args
    try:
        resized = resize_and_center_face(image_path, size)
        if not resized:
            return (False, image_path, None)

        stem, ext = Path(image_path).stem, Path(image_path).suffix
        output_path = Path(output_folder) / f"{stem}.out{ext}"
        resized.save(output_path)
        logger.info(f"Saved: {output_path}")
        return (True, image_path, str(output_path))
    except Exception as e:
        logger.error(f"Error saving {image_path}: {e}")
        return (False, image_path, None)


def process_images(input_path, size=224, output_folder=None, workers=None):
    """
    Process multiple images with face detection and resizing.

    Args:
        input_path: Path to image file or directory
        size: Output size in pixels (square)
        output_folder: Output directory (default: ./output)
        workers: Number of worker processes (None = auto)

    Returns:
        Tuple of (successful_count, failed_count)
    """
    input_path = Path(input_path)
    is_directory = input_path.is_dir()

    if is_directory:
        if not input_path.exists():
            logger.error(f"Directory not found: {input_path}")
            return (0, 0)

        image_paths = [str(p) for p in input_path.iterdir()
                      if p.is_file() and is_valid_image(str(p))]

        if not image_paths:
            logger.error(f"No valid images in {input_path}")
            logger.info(f"Supported: {', '.join(SUPPORTED_FORMATS)}")
            return (0, 0)

        logger.info(f"Found {len(image_paths)} image(s)")
    else:
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return (0, 0)
        if not is_valid_image(str(input_path)):
            logger.error(f"Unsupported format: {input_path}")
            return (0, 0)
        image_paths = [str(input_path)]

    if output_folder is None:
        output_folder = input_path / "output" if is_directory else input_path.parent / "output"
    else:
        output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    workers = workers or min(cpu_count(), len(image_paths))
    logger.info(f"Processing with {workers} worker(s)")

    args_list = [(path, size, str(output_folder)) for path in image_paths]

    if workers == 1 or len(image_paths) == 1:
        results = [_process_single(args) for args in tqdm(args_list, desc="Processing", unit="img")]
    else:
        with Pool(workers) as pool:
            results = list(tqdm(pool.imap(_process_single, args_list),
                              total=len(args_list), desc="Processing", unit="img"))

    successful = sum(1 for r in results if r[0])
    failed = len(results) - successful

    logger.info(f"Processed: {successful}/{len(image_paths)}")

    for success, path, _ in results:
        if not success:
            logger.warning(f"Failed: {path}")

    return (successful, failed)
