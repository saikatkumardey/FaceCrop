"""Tests for core functionality."""

import shutil
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from facecrop.core import (
    SUPPORTED_FORMATS,
    is_valid_image,
    process_images,
    resize_and_center_face,
)


class TestImageValidation:
    """Test image format validation."""

    def test_valid_image_formats(self):
        """Test that supported formats are recognized."""
        assert is_valid_image("test.jpg")
        assert is_valid_image("test.jpeg")
        assert is_valid_image("test.png")
        assert is_valid_image("test.bmp")
        assert is_valid_image("test.webp")
        assert is_valid_image("test.tiff")
        assert is_valid_image("test.tif")

    def test_invalid_image_formats(self):
        """Test that unsupported formats are rejected."""
        assert not is_valid_image("test.txt")
        assert not is_valid_image("test.pdf")
        assert not is_valid_image("test.doc")
        assert not is_valid_image("README.md")
        assert not is_valid_image("script.py")

    def test_case_insensitive(self):
        """Test that format checking is case-insensitive."""
        assert is_valid_image("test.JPG")
        assert is_valid_image("test.PNG")
        assert is_valid_image("test.JPEG")


class TestResizeAndCenterFace:
    """Test face detection and resizing."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)

    @pytest.fixture
    def sample_image(self, temp_dir):
        """Create a sample test image."""
        img_path = Path(temp_dir) / "test.png"
        # Create a simple 500x500 white image
        img = Image.new('RGB', (500, 500), color='white')
        img.save(img_path)
        return str(img_path)

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        result = resize_and_center_face("nonexistent.jpg", 224)
        assert result is None

    def test_invalid_format(self, temp_dir):
        """Test handling of invalid file formats."""
        txt_file = Path(temp_dir) / "test.txt"
        txt_file.write_text("not an image")
        result = resize_and_center_face(str(txt_file), 224)
        assert result is None

    def test_resize_basic_image(self, sample_image):
        """Test basic image resizing."""
        result = resize_and_center_face(sample_image, 224)
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == (224, 224)

    def test_different_sizes(self, sample_image):
        """Test resizing to different dimensions."""
        for size in [64, 128, 224, 512]:
            result = resize_and_center_face(sample_image, size)
            assert result is not None
            assert result.size == (size, size)


class TestProcessImages:
    """Test batch image processing."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)

    @pytest.fixture
    def sample_images_dir(self, temp_dir):
        """Create directory with sample images."""
        input_dir = Path(temp_dir) / "input"
        input_dir.mkdir()

        # Create 3 test images
        for i in range(3):
            img = Image.new('RGB', (400, 400), color=(i*80, i*80, i*80))
            img.save(input_dir / f"test_{i}.png")

        # Create a non-image file (should be ignored)
        (input_dir / "README.txt").write_text("not an image")

        return str(input_dir)

    def test_process_directory(self, sample_images_dir, temp_dir):
        """Test processing entire directory."""
        output_dir = Path(temp_dir) / "output"

        successful, failed = process_images(
            sample_images_dir,
            size=224,
            output_folder=str(output_dir),
            workers=1
        )

        assert successful == 3
        assert failed == 0
        assert output_dir.exists()
        assert len(list(output_dir.glob("*.png"))) == 3

    def test_process_single_file(self, sample_images_dir, temp_dir):
        """Test processing single image file."""
        input_file = Path(sample_images_dir) / "test_0.png"
        output_dir = Path(temp_dir) / "output"

        successful, failed = process_images(
            str(input_file),
            size=128,
            output_folder=str(output_dir),
            workers=1
        )

        assert successful == 1
        assert failed == 0

    def test_nonexistent_directory(self):
        """Test handling of nonexistent directory."""
        successful, failed = process_images(
            "/nonexistent/path",
            size=224
        )
        assert successful == 0
        assert failed == 0

    def test_empty_directory(self, temp_dir):
        """Test handling of empty directory."""
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()

        successful, failed = process_images(
            str(empty_dir),
            size=224
        )
        assert successful == 0
        assert failed == 0

    def test_multiprocessing(self, sample_images_dir, temp_dir):
        """Test multiprocessing with multiple workers."""
        output_dir = Path(temp_dir) / "output"

        successful, failed = process_images(
            sample_images_dir,
            size=224,
            output_folder=str(output_dir),
            workers=2
        )

        assert successful == 3
        assert failed == 0


class TestConstants:
    """Test package constants."""

    def test_supported_formats(self):
        """Test that SUPPORTED_FORMATS contains expected values."""
        assert '.jpg' in SUPPORTED_FORMATS
        assert '.jpeg' in SUPPORTED_FORMATS
        assert '.png' in SUPPORTED_FORMATS
        assert '.bmp' in SUPPORTED_FORMATS
        assert '.webp' in SUPPORTED_FORMATS
        assert isinstance(SUPPORTED_FORMATS, set)
