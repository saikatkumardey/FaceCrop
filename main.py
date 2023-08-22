
import os
import argparse
import dlib
from PIL import Image
import cv2
from pathlib import Path

# Load face detection model
detector = dlib.get_frontal_face_detector()

def resize_and_center_face(image_path, size):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = detector(image_rgb)
    if len(faces) > 0:
        print(f"Found {len(faces)} faces in {image_path}")
        face = faces[0]
        center_x = (face.left() + face.right()) // 2
        center_y = (face.top() + face.bottom()) // 2
    else:
        print("Warning: No faces found.")
        center_x = image.shape[1] // 2
        center_y = image.shape[0] // 2

    left = max(center_x - size // 2, 0)
    top = max(center_y - size // 2, 0)
    right = min(center_x + size // 2, image.shape[1])
    bottom = min(center_y + size // 2, image.shape[0])

    cropped_image = image[top:bottom, left:right]
    resized_image = cv2.resize(cropped_image, (size, size))
    pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
    return pil_image

def bulk_resize(input_path, size, output_folder, is_directory=True):
    if is_directory:
        image_paths = [os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
    else:
        image_paths = [input_path]

    if output_folder is None:
            output_folder = Path(os.path.dirname(image_paths[0])) / "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for image_path in image_paths:
        resized_image = resize_and_center_face(image_path, size)
        name, extension = os.path.splitext(os.path.basename(image_path))
        output_name = name + ".out" + extension
        output_path = os.path.join(output_folder, output_name)
        resized_image.save(output_path)
        print(f"Image saved to {output_path}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Bulk Image Resizer")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--dir', help='Path to directory containing images', type=str)
    input_group.add_argument('--file', help='Path to single image file', type=str)
    parser.add_argument('--output', help='Path to output directory', type=str)
    parser.add_argument('--size', help='Size of the output square image',default=224, type=int)

    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.output and not os.path.exists(args.output):
        os.makedirs(args.output)

    if args.dir:
        input_path = args.dir
        is_directory = True
    else:
        input_path = args.file
        is_directory = False

    bulk_resize(input_path, args.size, args.output, is_directory)

if __name__ == '__main__':
    main()
