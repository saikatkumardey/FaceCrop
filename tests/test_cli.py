"""Tests for CLI functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image

from facecrop.cli import parse_args, main
from facecrop import __version__


class TestParseArgs:
    """Test argument parsing."""

    def test_single_file_argument(self):
        """Test parsing single file argument."""
        args = parse_args(['image.jpg'])
        assert args.input == 'image.jpg'
        assert args.size == 224
        assert args.output is None
        assert args.workers is None

    def test_directory_argument(self):
        """Test parsing directory argument."""
        args = parse_args(['photos/'])
        assert args.input == 'photos/'

    def test_output_flag(self):
        """Test output directory flag."""
        args = parse_args(['image.jpg', '--output', 'results/'])
        assert args.output == 'results/'

        args = parse_args(['image.jpg', '-o', 'out/'])
        assert args.output == 'out/'

    def test_size_flag(self):
        """Test size flag."""
        args = parse_args(['image.jpg', '--size', '512'])
        assert args.size == 512

        args = parse_args(['image.jpg', '-s', '128'])
        assert args.size == 128

    def test_workers_flag(self):
        """Test workers flag."""
        args = parse_args(['image.jpg', '--workers', '4'])
        assert args.workers == 4

        args = parse_args(['image.jpg', '-w', '8'])
        assert args.workers == 8

    def test_quiet_flag(self):
        """Test quiet flag."""
        args = parse_args(['image.jpg', '--quiet'])
        assert args.quiet is True

        args = parse_args(['image.jpg', '-q'])
        assert args.quiet is True

    def test_version(self, capsys):
        """Test version flag."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(['--version'])
        assert exc_info.value.code == 0

    def test_help(self, capsys):
        """Test help flag."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(['--help'])
        assert exc_info.value.code == 0

    def test_missing_input(self):
        """Test missing required input argument."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestMain:
    """Test main CLI function."""

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
        img = Image.new('RGB', (400, 400), color='white')
        img.save(img_path)
        return str(img_path)

    def test_successful_processing(self, sample_image, temp_dir):
        """Test successful image processing."""
        output_dir = Path(temp_dir) / "output"
        exit_code = main([sample_image, '-o', str(output_dir), '-s', '224'])
        assert exit_code == 0
        assert output_dir.exists()

    def test_nonexistent_input(self):
        """Test handling of nonexistent input."""
        exit_code = main(['/nonexistent/image.jpg'])
        assert exit_code == 1

    def test_invalid_size(self, sample_image):
        """Test handling of invalid size."""
        exit_code = main([sample_image, '--size', '50'])  # Too small
        assert exit_code == 1

        exit_code = main([sample_image, '--size', '5000'])  # Too large
        assert exit_code == 1

    def test_invalid_workers(self, sample_image):
        """Test handling of invalid workers."""
        exit_code = main([sample_image, '--workers', '0'])
        assert exit_code == 1

        exit_code = main([sample_image, '--workers', '-1'])
        assert exit_code == 1

    def test_keyboard_interrupt(self, sample_image, monkeypatch):
        """Test handling of keyboard interrupt."""
        def mock_process(*args, **kwargs):
            raise KeyboardInterrupt()

        import facecrop.cli
        monkeypatch.setattr(facecrop.cli, 'process_images', mock_process)

        exit_code = main([sample_image])
        assert exit_code == 130


class TestCLIIntegration:
    """Integration tests for CLI."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)

    @pytest.fixture
    def sample_dir(self, temp_dir):
        """Create directory with sample images."""
        input_dir = Path(temp_dir) / "input"
        input_dir.mkdir()

        for i in range(2):
            img = Image.new('RGB', (300, 300), color=(i*100, i*100, i*100))
            img.save(input_dir / f"img_{i}.png")

        return str(input_dir)

    def test_full_workflow(self, sample_dir, temp_dir):
        """Test complete CLI workflow."""
        output_dir = Path(temp_dir) / "results"

        exit_code = main([
            sample_dir,
            '--output', str(output_dir),
            '--size', '256',
            '--workers', '1'
        ])

        assert exit_code == 0
        assert output_dir.exists()
        output_files = list(output_dir.glob("*.png"))
        assert len(output_files) == 2

        # Verify output dimensions
        for file in output_files:
            img = Image.open(file)
            assert img.size == (256, 256)
