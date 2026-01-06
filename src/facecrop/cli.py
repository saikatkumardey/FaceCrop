"""Command-line interface for FaceCrop."""

import sys
import argparse
from pathlib import Path
from loguru import logger

from . import __version__
from .core import process_images


def setup_logging():
    """Configure loguru logger."""
    logger.add("facecrop.log", rotation="10 MB", level="INFO")


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="facecrop",
        description="FaceCrop: Face-centered intelligent image resizing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  facecrop image.jpg                    # Process single image
  facecrop photos/                      # Process directory
  facecrop photos/ --size 512           # Custom output size
  facecrop photos/ --workers 8          # Use 8 CPU cores
  facecrop image.jpg --output results/  # Custom output directory

Supported formats: jpg, jpeg, png, bmp, webp, tiff, tif
        """
    )

    parser.add_argument(
        'input',
        help='Path to image file or directory'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: ./output)',
        dest='output'
    )
    parser.add_argument(
        '-s', '--size',
        type=int,
        default=224,
        help='Output size in pixels (default: 224)'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of worker processes (default: auto)'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )

    return parser.parse_args(args)


def main(args=None):
    """Main entry point for CLI."""
    setup_logging()

    parsed_args = parse_args(args)

    # Validate size
    if not 64 <= parsed_args.size <= 4096:
        logger.error(f"Size must be 64-4096, got {parsed_args.size}")
        return 1

    # Validate workers
    if parsed_args.workers is not None and parsed_args.workers < 1:
        logger.error(f"Workers must be >= 1, got {parsed_args.workers}")
        return 1

    # Validate input exists
    if not Path(parsed_args.input).exists():
        logger.error(f"Input not found: {parsed_args.input}")
        return 1

    try:
        logger.info(f"FaceCrop v{__version__}")

        successful, failed = process_images(
            parsed_args.input,
            size=parsed_args.size,
            output_folder=parsed_args.output,
            workers=parsed_args.workers
        )

        if failed > 0:
            logger.warning(f"Complete with {failed} failures")
            return 1
        else:
            logger.info("Complete")
            return 0

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
