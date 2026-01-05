
import os
import argparse
import dlib
from PIL import Image
import cv2
from pathlib import Path
import logging
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('facecrop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load face detection model
detector = dlib.get_frontal_face_detector()

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}

def is_valid_image(file_path):
    """Check if file is a supported image format."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_FORMATS

def resize_and_center_face(image_path, size):
    """
    Resize and center image on detected face.
    Returns PIL Image on success, None on failure.
    """
    try:
        # Validate input
        if not os.path.exists(image_path):
            logger.error(f"File does not exist: {image_path}")
            return None

        if not is_valid_image(image_path):
            logger.error(f"Unsupported file format: {image_path}")
            return None

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return None

        # Check if image is too small
        if image.shape[0] < size or image.shape[1] < size:
            logger.warning(f"Image {image_path} is smaller than target size {size}x{size}")

        # Convert to RGB for face detection
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        faces = detector(image_rgb)

        if len(faces) > 0:
            logger.info(f"Found {len(faces)} face(s) in {os.path.basename(image_path)}")
            face = faces[0]
            center_x = (face.left() + face.right()) // 2
            center_y = (face.top() + face.bottom()) // 2
        else:
            logger.warning(f"No faces found in {os.path.basename(image_path)}, using center crop")
            center_x = image.shape[1] // 2
            center_y = image.shape[0] // 2

        # Calculate crop boundaries
        left = max(center_x - size // 2, 0)
        top = max(center_y - size // 2, 0)
        right = min(center_x + size // 2, image.shape[1])
        bottom = min(center_y + size // 2, image.shape[0])

        # Crop and resize
        cropped_image = image[top:bottom, left:right]

        # Handle edge case where crop is empty
        if cropped_image.size == 0:
            logger.error(f"Crop resulted in empty image: {image_path}")
            return None

        resized_image = cv2.resize(cropped_image, (size, size))
        pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
        return pil_image

    except Exception as e:
        logger.error(f"Error processing {image_path}: {str(e)}")
        return None

def process_single_image(args):
    """
    Process a single image. Wrapper function for multiprocessing.
    Returns tuple: (success: bool, input_path: str, output_path: str or None)
    """
    image_path, size, output_folder = args

    try:
        resized_image = resize_and_center_face(image_path, size)

        if resized_image is None:
            return (False, image_path, None)

        # Generate output filename
        name, extension = os.path.splitext(os.path.basename(image_path))
        output_name = name + ".out" + extension
        output_path = os.path.join(output_folder, output_name)

        # Save image
        resized_image.save(output_path)
        logger.info(f"Saved: {output_path}")

        return (True, image_path, output_path)

    except Exception as e:
        logger.error(f"Error saving {image_path}: {str(e)}")
        return (False, image_path, None)

def bulk_resize(input_path, size, output_folder, is_directory=True, workers=None):
    """
    Process multiple images with optional multiprocessing.

    Args:
        input_path: Directory path or single file path
        size: Target output size (square)
        output_folder: Output directory
        is_directory: True if input_path is a directory
        workers: Number of worker processes (None = use all CPUs)
    """
    # Get list of image paths
    if is_directory:
        if not os.path.exists(input_path):
            logger.error(f"Directory does not exist: {input_path}")
            return

        all_files = [os.path.join(input_path, f) for f in os.listdir(input_path)]
        # Filter only valid image files
        image_paths = [f for f in all_files if os.path.isfile(f) and is_valid_image(f)]

        if not image_paths:
            logger.error(f"No valid image files found in {input_path}")
            logger.info(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            return

        logger.info(f"Found {len(image_paths)} valid image(s) in {input_path}")
    else:
        if not os.path.exists(input_path):
            logger.error(f"File does not exist: {input_path}")
            return

        if not is_valid_image(input_path):
            logger.error(f"Unsupported file format: {input_path}")
            logger.info(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            return

        image_paths = [input_path]

    # Setup output folder
    if output_folder is None:
        if is_directory:
            output_folder = Path(input_path) / "output"
        else:
            output_folder = Path(os.path.dirname(input_path)) / "output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Created output folder: {output_folder}")

    # Determine number of workers
    if workers is None:
        workers = min(cpu_count(), len(image_paths))  # Don't use more workers than images

    logger.info(f"Processing {len(image_paths)} image(s) with {workers} worker(s)")

    # Prepare arguments for processing
    args_list = [(path, size, output_folder) for path in image_paths]

    # Process images
    if workers == 1 or len(image_paths) == 1:
        # Single-threaded processing
        results = []
        for args in tqdm(args_list, desc="Processing images", unit="img"):
            results.append(process_single_image(args))
    else:
        # Multi-threaded processing
        with Pool(workers) as pool:
            results = list(tqdm(
                pool.imap(process_single_image, args_list),
                total=len(args_list),
                desc="Processing images",
                unit="img"
            ))

    # Summary
    successful = [r for r in results if r[0]]
    failed = [r for r in results if not r[0]]

    logger.info(f"Successfully processed: {len(successful)}/{len(image_paths)} images")
    if failed:
        logger.warning(f"Failed to process {len(failed)} image(s)")
        for _, failed_path, _ in failed:
            logger.warning(f"  - {failed_path}")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="FaceCrop: Intelligent face-centered image resizing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a directory
  python main.py --dir ./images --size 224

  # Process a single file
  python main.py --file photo.jpg --output ./results

  # Use specific number of CPU cores
  python main.py --dir ./images --workers 4

Supported formats: jpg, jpeg, png, bmp, webp, tiff, tif
        """
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--dir', help='Path to directory containing images', type=str)
    input_group.add_argument('--file', help='Path to single image file', type=str)

    parser.add_argument('--output', help='Path to output directory (default: ./output)', type=str)
    parser.add_argument('--size', help='Size of the output square image (default: 224)',
                        default=224, type=int)
    parser.add_argument('--workers', help='Number of worker processes (default: use all CPUs)',
                        type=int, default=None)

    return parser.parse_args()

def validate_arguments(args):
    """Validate command-line arguments."""
    # Validate size
    if args.size < 64 or args.size > 4096:
        logger.error(f"Size must be between 64 and 4096, got {args.size}")
        return False

    # Validate workers
    if args.workers is not None and args.workers < 1:
        logger.error(f"Workers must be at least 1, got {args.workers}")
        return False

    # Check if input path exists
    input_path = args.dir or args.file
    if not os.path.exists(input_path):
        logger.error(f"Input path does not exist: {input_path}")
        return False

    return True

def main():
    """Main entry point."""
    logger.info("FaceCrop starting...")

    args = parse_arguments()

    # Validate arguments
    if not validate_arguments(args):
        return 1

    # Create output directory if specified
    if args.output and not os.path.exists(args.output):
        os.makedirs(args.output)
        logger.info(f"Created output directory: {args.output}")

    # Determine input type
    if args.dir:
        input_path = args.dir
        is_directory = True
    else:
        input_path = args.file
        is_directory = False

    # Process images
    try:
        bulk_resize(input_path, args.size, args.output, is_directory, args.workers)
        logger.info("Processing complete!")
        return 0
    except KeyboardInterrupt:
        logger.warning("Processing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())
