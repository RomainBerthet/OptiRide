# Contributing to OptiRide

First off, thank you for considering contributing to OptiRide! It's people like you that make OptiRide such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (GPX files, configuration, command lines)
- **Describe the behavior you observed and what you expected**
- **Include screenshots or animated GIFs** if relevant
- **Include your environment details** (OS, Python version, package version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions or features** you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/optiride.git
cd optiride

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev,docs,jupyter]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### Code Style

We use modern Python tooling for consistent code quality:

- **Ruff**: For linting and formatting
- **MyPy**: For static type checking
- **Pre-commit**: For automated checks

```bash
# Format code
ruff format .

# Lint and fix issues
ruff check . --fix

# Type check
mypy optiride

# Run all pre-commit hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=optiride --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_physics.py

# Run tests matching a pattern
pytest -k "test_power"

# Run only unit tests (fast)
pytest -m unit

# Run integration tests
pytest -m integration
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_power_required_flat_terrain()`
- Add docstrings to complex tests
- Use fixtures for common setup
- Mark slow tests: `@pytest.mark.slow`
- Mark integration tests: `@pytest.mark.integration`

Example test:

```python
import pytest
from optiride import RiderBike, Environment, power_required


def test_power_required_flat_terrain():
    """Test power calculation on flat terrain with no wind."""
    rider = RiderBike(
        mass_rider_kg=72.0,
        mass_bike_kg=8.0,
        crr=0.0035,
        cda=0.30,
        drivetrain_eff=0.97,
    )
    env = Environment(air_density=1.225)

    power = power_required(
        v_ms=10.0,
        slope_tan=0.0,
        bearing_deg=0.0,
        rb=rider,
        env=env,
    )

    # Sanity check: reasonable power range
    assert 150 < power < 200
```

### Documentation

- Use Google-style docstrings for all public APIs
- Include examples in docstrings where helpful
- Update README.md for user-facing changes
- Add type hints to all functions

Example docstring:

```python
def calculate_speed(power_w: float, slope: float) -> float:
    """Calculate achievable speed for given power and slope.

    Args:
        power_w: Available power in watts.
        slope: Grade as a fraction (e.g., 0.05 for 5%).

    Returns:
        Achievable speed in meters per second.

    Raises:
        ValueError: If power is negative.

    Example:
        >>> speed = calculate_speed(250.0, 0.03)
        >>> speed > 0
        True
    """
```

## Project Structure

```
optiride/
├── optiride/           # Main package
│   ├── __init__.py     # Public API exports
│   ├── models.py       # Data models
│   ├── physics.py      # Physics calculations
│   ├── optimizer.py    # Pacing optimization
│   ├── gpxio.py        # GPX file handling
│   ├── weather.py      # Weather API integration
│   ├── nutrition.py    # Nutrition planning
│   ├── exporter.py     # Output file generation
│   ├── env.py          # Environmental calculations
│   └── cli.py          # Command-line interface
├── tests/              # Test suite
├── examples/           # Example GPX files and notebooks
├── docs/               # Documentation
└── pyproject.toml      # Project configuration
```

## Commit Messages

We follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(weather): add support for custom weather APIs

docs: update installation instructions

fix(physics): correct wind direction calculation

test(optimizer): add tests for W' depletion
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag: `git tag -a v0.2.0 -m "Release 0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release from tag
6. Build and publish to PyPI

## Questions?

Feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Join our community discussions

Thank you for contributing to OptiRide! 🚴
