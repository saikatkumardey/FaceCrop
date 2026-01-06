# Contributing to FaceCrop

Thank you for your interest in contributing to FaceCrop! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/saikatkumardey/FaceCrop/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, package versions)
   - Code samples or screenshots if applicable

### Suggesting Features

1. Check existing [Issues](https://github.com/saikatkumardey/FaceCrop/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   gh repo fork saikatkumardey/FaceCrop --clone
   cd FaceCrop
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Make your changes**
   - Write clear, documented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

5. **Run tests and linters**
   ```bash
   # Format code
   black src/ tests/

   # Lint
   ruff check src/ tests/

   # Type check
   mypy src/

   # Run tests
   pytest
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

   Use clear, descriptive commit messages:
   - `feat: Add support for GIF format`
   - `fix: Handle empty directories correctly`
   - `docs: Update installation instructions`
   - `test: Add tests for edge cases`

7. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Create a Pull Request**
   - Provide clear description of changes
   - Reference related issues
   - Ensure CI checks pass

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Format with `black`
- Lint with `ruff`

### Testing

- Write tests for all new features
- Maintain >80% code coverage
- Test edge cases and error conditions
- Use descriptive test names

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update CLAUDE.md for architecture changes
- Include code examples where helpful

### Commit Messages

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

## Development Workflow

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=facecrop

# Specific test file
pytest tests/test_core.py

# Specific test
pytest tests/test_core.py::test_resize_and_center_face
```

### Building Locally

```bash
# Build package
python -m build

# Install locally
pip install -e .

# Test CLI
facecrop --help
```

### Release Process

1. Update version in `src/facecrop/__init__.py`
2. Update CHANGELOG.md
3. Create release PR
4. After merge, tag release
5. GitHub Actions handles PyPI upload

## Project Structure

```
FaceCrop/
├── src/facecrop/          # Main package
│   ├── __init__.py        # Package metadata
│   ├── cli.py             # CLI interface
│   ├── core.py            # Core functionality
│   └── __main__.py        # Entry point
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/workflows/     # CI/CD
├── pyproject.toml         # Package configuration
└── README.md              # Main documentation
```

## Questions?

Feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Check existing documentation

Thank you for contributing! 🎉
