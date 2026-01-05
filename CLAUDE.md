# CLAUDE.md - AI Assistant Guide for FaceCrop

## Project Overview

**FaceCrop** is a Python-based CLI tool for intelligent image resizing that centers on detected faces. It provides both single-image and bulk processing capabilities, ensuring that faces remain the focal point when images are cropped and resized to square dimensions.

### Key Capabilities
- Face-centered intelligent cropping using dlib face detection
- Bulk processing of image directories
- Single image processing
- Configurable output size (default: 224x224)
- Automatic fallback to center-crop when no face is detected

## Codebase Structure

```
FaceCrop/
├── main.py              # Main application code (single file project)
├── README.md            # User-facing documentation
├── LICENSE.md           # MIT License
├── .gitignore          # Python-standard gitignore
└── example/            # Sample images and outputs
    ├── example-1.png
    ├── example-2.png
    ├── example-3.jpeg
    └── output/         # Example output directory
        ├── example-1.out.png
        ├── example-2.out.png
        └── example-3.out.jpeg
```

### Project Characteristics
- **Language**: Python 3.x
- **Architecture**: Simple single-file CLI application
- **Dependencies**: opencv-python, dlib, Pillow
- **License**: MIT
- **No package structure**: All code is in `main.py`

## Core Dependencies

### Required Libraries
1. **dlib** - Face detection (HOG-based frontal face detector)
2. **opencv-python (cv2)** - Image processing and manipulation
3. **Pillow (PIL)** - Image I/O and format handling
4. **argparse** - CLI argument parsing (stdlib)
5. **pathlib** - Path handling (stdlib)

### Installation
```bash
pip install opencv-python dlib Pillow
```

**Note**: dlib can be complex to install on some systems due to C++ compilation requirements. Users may need cmake and C++ build tools.

## Code Architecture (main.py)

### Key Functions

#### 1. `resize_and_center_face(image_path, size)`
**Location**: main.py:12-34

**Purpose**: Core image processing function that detects faces and crops/resizes images.

**Logic Flow**:
1. Load image using cv2.imread()
2. Convert BGR to RGB for dlib compatibility
3. Run face detection using dlib.get_frontal_face_detector()
4. If face found:
   - Calculate center point of first detected face
   - Use face center for crop anchor
5. If no face found:
   - Print warning
   - Use image center as fallback
6. Calculate crop boundaries (with bounds checking)
7. Crop and resize to target size
8. Convert back to RGB and return PIL Image

**Returns**: PIL.Image object

**Important Notes**:
- Uses only the **first** detected face (faces[0]) even if multiple faces found
- Maintains aspect ratio by cropping to square before resizing
- Edge cases handled: ensures crop doesn't exceed image boundaries

#### 2. `bulk_resize(input_path, size, output_folder, is_directory=True)`
**Location**: main.py:36-53

**Purpose**: Handles both single and batch image processing.

**Logic Flow**:
1. Build list of image paths (directory listing or single file)
2. Create output folder if not specified (defaults to "output" subdirectory)
3. Process each image through resize_and_center_face()
4. Save with ".out" inserted before extension (e.g., "image.jpg" → "image.out.jpg")

**Output Naming Convention**: `{original_name}.out{extension}`

#### 3. `parse_arguments()`
**Location**: main.py:55-63

**Purpose**: Define and parse CLI arguments.

**Arguments**:
- `--dir`: Directory path (mutually exclusive with --file)
- `--file`: Single file path (mutually exclusive with --dir)
- `--output`: Optional output directory
- `--size`: Optional square size (default: 224)

#### 4. `main()`
**Location**: main.py:65-78

**Purpose**: Entry point that orchestrates the workflow.

## Development Workflows

### Running the Tool

**Process a directory**:
```bash
python main.py --dir /path/to/images --output /path/to/output --size 224
```

**Process a single file**:
```bash
python main.py --file /path/to/image.jpg --output /path/to/output --size 224
```

**Minimal usage** (uses defaults):
```bash
python main.py --dir ./example
```

### Git Workflow
- **Main Branch**: Default branch for releases
- **Feature Branches**: Use `claude/` prefix for AI-generated changes
- **Commit Style**: Clear, descriptive messages focusing on the "why"
- **License**: MIT - permissive for modifications

## Code Conventions and Style

### Python Style
- **Style Guide**: Generally follows PEP 8
- **Indentation**: 4 spaces
- **Imports**: Grouped at top (stdlib, then third-party)
- **Variable naming**: snake_case
- **Constants**: Could benefit from UPPER_CASE (currently inline)

### Current Code Patterns
1. **Global detector initialization**: `detector = dlib.get_frontal_face_detector()` at module level
2. **Error handling**: Minimal - assumes valid image paths and formats
3. **Logging**: Print statements for user feedback
4. **File handling**: No explicit file validation or exception handling

### Areas for Improvement (if asked)
- Add input validation and error handling
- Support for additional image formats
- Progress bars for bulk operations
- Logging instead of print statements
- Unit tests
- Type hints (PEP 484)
- Configuration file support

## Testing Considerations

### Current State
- **No test suite**: No tests currently exist
- **Manual testing**: Use example/ directory for validation

### Test Data
- Sample images in `example/` directory
- Expected outputs in `example/output/`
- Mix of formats: PNG and JPEG

### Recommended Test Coverage (if implementing)
1. Face detection accuracy
2. No-face fallback behavior
3. Boundary conditions (very small/large images)
4. Multiple faces handling
5. Invalid input handling
6. Output file naming
7. Directory creation
8. Various image formats

## Common Tasks for AI Assistants

### When Modifying Code

1. **Read main.py first**: Always read the entire file before making changes
2. **Preserve simplicity**: This is intentionally a single-file tool
3. **Test with examples**: Use the example/ directory for validation
4. **Maintain CLI compatibility**: Don't break existing argument structure
5. **Consider edge cases**: Image boundaries, missing faces, invalid formats

### When Adding Features

**Good additions**:
- Better error handling and validation
- Support for more face detection backends
- Batch processing optimizations
- Configuration file support
- Progress indicators
- Multi-face handling options
- Padding options for crop boundaries

**Avoid**:
- Over-engineering with complex architectures
- Breaking backward compatibility
- Adding dependencies without justification
- Creating multiple files unless truly necessary

### When Debugging

**Common issues**:
1. **dlib installation failures**: Often needs cmake and build tools
2. **Memory issues**: Large images or directories
3. **Face detection misses**: Lighting, angles, partial faces
4. **Color space confusion**: cv2 uses BGR, dlib expects RGB
5. **Path handling**: Cross-platform path separators

**Debugging approach**:
1. Check face detection output (number of faces found)
2. Verify image loading (check cv2.imread() result)
3. Inspect crop boundaries (ensure within image bounds)
4. Test with example images first

### When Documenting

**Update README.md** when:
- Adding new CLI arguments
- Changing installation requirements
- Modifying default behaviors

**Update this file (CLAUDE.md)** when:
- Refactoring code structure
- Adding new functions
- Changing development workflows
- Adding new dependencies

## Important Conventions

### Image Processing Pipeline
```
Input Image → Load (cv2) → Convert BGR→RGB → Face Detection (dlib)
→ Calculate Crop Center → Crop → Resize → Convert RGB→BGR → Save (PIL)
```

### Output Structure
- Default output folder: `{input_directory}/output/`
- Output naming: `{original_name}.out{original_extension}`
- Preserved formats: Original format maintained (PNG→PNG, JPEG→JPEG)

### Face Detection Behavior
- Uses dlib's HOG-based detector (not CNN-based)
- Processes in RGB color space
- Only first face used if multiple detected
- No face = fallback to geometric center

## Environment Notes

### Python Version
- Requires: Python 3.x
- Stdlib features used: argparse, os, pathlib

### System Requirements
- Memory: Depends on image sizes
- CPU: dlib face detection is CPU-intensive
- Storage: Output images similar size to inputs

### Known Limitations
1. Only detects frontal faces (not profiles)
2. Performance scales with image count and resolution
3. No GPU acceleration
4. Limited error messages for invalid inputs
5. No progress indication for large batches

## Quick Reference

### File Locations
- Main code: `main.py`
- Examples: `example/`
- Documentation: `README.md` (user), `CLAUDE.md` (AI)
- License: `LICENSE.md`

### Key Line Numbers (main.py)
- Face detector initialization: Line 10
- Core processing function: Lines 12-34
- Bulk processing: Lines 36-53
- CLI parsing: Lines 55-63
- Entry point: Lines 65-78

### Default Values
- Output size: 224 pixels (square)
- Output directory: `{input_dir}/output/`
- Face selection: First face only

---

**Last Updated**: 2026-01-05
**Repository**: FaceCrop
**Purpose**: Guide AI assistants in understanding and modifying this codebase effectively
