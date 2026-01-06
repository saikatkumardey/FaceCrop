"""FaceCrop: Face-centered intelligent image resizing."""

__version__ = "0.1.0"
__author__ = "FaceCrop Contributors"
__license__ = "MIT"

from .core import resize_and_center_face, process_images

__all__ = ["resize_and_center_face", "process_images", "__version__"]
