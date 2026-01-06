"""FaceCrop: Face-centered intelligent image resizing."""

from .core import process_images, resize_and_center_face

__version__ = "0.1.0"
__author__ = "FaceCrop Contributors"
__license__ = "MIT"

__all__ = ["resize_and_center_face", "process_images", "__version__"]
