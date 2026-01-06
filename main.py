import os
import argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count
import dlib
import cv2
from PIL import Image
from tqdm import tqdm
from loguru import logger

logger.add("facecrop.log", rotation="10 MB")

detector = dlib.get_frontal_face_detector()
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}

def is_valid_image(path):
    return Path(path).suffix.lower() in SUPPORTED_FORMATS

def resize_and_center_face(image_path, size):
    try:
        if not Path(image_path).exists():
            logger.error(f"File not found: {image_path}")
            return None

        if not is_valid_image(image_path):
            logger.error(f"Unsupported format: {image_path}")
            return None

        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read: {image_path}")
            return None

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = detector(image_rgb)

        if faces:
            logger.info(f"Found {len(faces)} face(s) in {Path(image_path).name}")
            face = faces[0]
            center_x, center_y = (face.left() + face.right()) // 2, (face.top() + face.bottom()) // 2
        else:
            logger.warning(f"No faces found in {Path(image_path).name}, using center crop")
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

def process_single_image(args):
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

def bulk_resize(input_path, size, output_folder, is_directory=True, workers=None):
    if is_directory:
        if not Path(input_path).exists():
            logger.error(f"Directory not found: {input_path}")
            return

        image_paths = [str(p) for p in Path(input_path).iterdir()
                      if p.is_file() and is_valid_image(str(p))]

        if not image_paths:
            logger.error(f"No valid images in {input_path}")
            logger.info(f"Supported: {', '.join(SUPPORTED_FORMATS)}")
            return

        logger.info(f"Found {len(image_paths)} image(s)")
    else:
        if not Path(input_path).exists():
            logger.error(f"File not found: {input_path}")
            return
        if not is_valid_image(input_path):
            logger.error(f"Unsupported format: {input_path}")
            return
        image_paths = [input_path]

    output_folder = Path(output_folder or (Path(input_path) / "output" if is_directory else Path(input_path).parent / "output"))
    output_folder.mkdir(parents=True, exist_ok=True)

    workers = workers or min(cpu_count(), len(image_paths))
    logger.info(f"Processing with {workers} worker(s)")

    args_list = [(path, size, str(output_folder)) for path in image_paths]

    if workers == 1 or len(image_paths) == 1:
        results = [process_single_image(args) for args in tqdm(args_list, desc="Processing", unit="img")]
    else:
        with Pool(workers) as pool:
            results = list(tqdm(pool.imap(process_single_image, args_list),
                              total=len(args_list), desc="Processing", unit="img"))

    successful = sum(1 for r in results if r[0])
    logger.info(f"Processed: {successful}/{len(image_paths)}")

    for success, path, _ in results:
        if not success:
            logger.warning(f"Failed: {path}")

def main():
    parser = argparse.ArgumentParser(
        description="FaceCrop: Face-centered image resizing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Supported formats: jpg, jpeg, png, bmp, webp, tiff, tif"
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--dir', help='Directory path')
    input_group.add_argument('--file', help='File path')
    parser.add_argument('--output', help='Output directory')
    parser.add_argument('--size', type=int, default=224, help='Output size (default: 224)')
    parser.add_argument('--workers', type=int, help='Worker processes (default: auto)')

    args = parser.parse_args()

    if not 64 <= args.size <= 4096:
        logger.error(f"Size must be 64-4096, got {args.size}")
        return 1

    if args.workers and args.workers < 1:
        logger.error(f"Workers must be >= 1, got {args.workers}")
        return 1

    try:
        logger.info("FaceCrop starting")
        bulk_resize(args.dir or args.file, args.size, args.output,
                   is_directory=bool(args.dir), workers=args.workers)
        logger.info("Complete")
        return 0
    except KeyboardInterrupt:
        logger.warning("Interrupted")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
