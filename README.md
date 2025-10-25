# 🚴 OptiRide

<div align="center">

**Professional cycling pacing optimizer using GPX data**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

[Features](#-features) •
[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

---

## 🎯 Overview

**OptiRide** is a powerful Python toolkit for optimizing cycling performance through intelligent pacing strategies. By analyzing GPX route data and combining it with rider characteristics, bike specifications, and weather conditions, OptiRide computes optimal power targets, estimates ride times, and generates comprehensive nutrition plans.

### Built on solid science

- **Physics engine**: Based on Martin et al. (1998) validated cycling power model
- **Power management**: Implements Critical Power (CP) and W' (W-prime) constraints
- **Weather integration**: Real-time weather data from Open-Meteo API
- **Wind modeling**: Accurate wind impact calculation based on bearing and relative airspeed

## ✨ Features

- 🎯 **Point-by-point power targets** optimized for terrain and conditions
- ⏱️ **Accurate time predictions** using physics-based modeling
- 🍎 **Nutrition & hydration planning** based on scientific guidelines
- 🌤️ **Automatic weather integration** with wind impact analysis
- 📊 **Rich visualizations** of elevation, power, and speed profiles
- 🕐 **Start time optimization** to find the best weather window
- 📁 **Multiple export formats** (CSV, GPX with power extensions, JSON)
- 🔬 **Type-safe & well-tested** with comprehensive docstrings

## 📦 Installation

### Using pip

```bash
pip install optiride
```

### Using pipx (recommended for CLI usage)

```bash
pipx install optiride
```

### From source

```bash
git clone https://github.com/romainberthet/optiride.git
cd optiride
pip install -e ".[dev]"
```

### Development installation

```bash
# Install with all development dependencies
pip install -e ".[dev,docs,jupyter]"

# Install pre-commit hooks
pre-commit install
```

## 🚀 Quick Start

### Basic usage

```bash
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 --bike-mass 8 \
  --cda 0.30 --crr 0.0035 \
  --ftp 260 --wprime 20000 \
  --power-flat 220
```

### With automatic weather

```bash
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 --bike-mass 8 \
  --cda 0.30 --crr 0.0035 \
  --ftp 260 --wprime 20000 \
  --power-flat 220 \
  --auto-weather --hour 9
```

### Optimize start time

Find the best time to start based on weather conditions:

```bash
optiride optimize-start \
  --gpx examples/sample.gpx \
  --mass 72 --bike-mass 8 \
  --cda 0.30 --crr 0.0035 \
  --ftp 260 --wprime 20000 \
  --power-flat 220 \
  --start-hour 6 --end-hour 20 \
  --export-gpx
```

### Output files

- `outputs/summary.json`: Comprehensive ride summary (time, kCal, nutrition plan)
- `outputs/targets.csv`: Detailed point-by-point targets (distance, slope, power, speed)
- `outputs/plots/*.png`: Elevation profile, power curve, speed profile
- `outputs/power_targets.gpx`: GPX file with power extensions (optional)

## 🐍 Python API

```python
import optiride as opr

# Define rider and bike
rider = opr.RiderBike(
    mass_rider_kg=72.0,
    mass_bike_kg=8.0,
    cda=0.30,
    crr=0.0035,
    ftp=260.0,
    w_prime_j=20000.0
)

# Set environment
env = opr.Environment(
    air_density=1.225,
    wind_u_ms=0.0,
    wind_v_ms=0.0
)

# Calculate required power for given speed
power = opr.power_required(
    v_ms=10.0,      # 36 km/h
    slope_tan=0.05,  # 5% grade
    bearing_deg=0.0,
    rb=rider,
    env=env
)

print(f"Required power: {power:.1f} W")
```

## 📚 Documentation

### Parameters Guide

#### Rider & Bike Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `--mass` | Rider weight (kg) | 60-90 |
| `--bike-mass` | Bike weight (kg) | 6-10 |
| `--cda` | Aerodynamic drag area (m²) | 0.20-0.40 |
| `--crr` | Rolling resistance coefficient | 0.002-0.005 |
| `--ftp` | Functional Threshold Power (W) | 200-400 |
| `--wprime` | Anaerobic capacity W' (J) | 15000-25000 |

#### Pacing Strategy

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--power-flat` | Base power on flat terrain (W) | Required |
| `--up-mult` | Power multiplier for climbs | 1.10 |
| `--down-mult` | Power multiplier for descents | 0.75 |
| `--max-delta` | Max power change between points (W) | 30.0 |

### Weather Integration

OptiRide can automatically fetch weather data from [Open-Meteo](https://open-meteo.com/) (no API key required):

```bash
optiride compute --gpx route.gpx --auto-weather --hour 10
```

This retrieves:
- Temperature
- Humidity
- Atmospheric pressure
- Wind speed and direction

Wind is projected onto the route bearing to calculate accurate aerodynamic drag.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=optiride --cov-report=html

# Run only unit tests
pytest -m unit
```

## 🛠️ Development

### Code Quality

This project uses modern Python tooling:

- **[Ruff](https://github.com/astral-sh/ruff)**: Lightning-fast linting and formatting
- **[MyPy](http://mypy-lang.org/)**: Static type checking
- **[Pytest](https://pytest.org/)**: Comprehensive testing framework
- **[Pre-commit](https://pre-commit.com/)**: Automated code quality checks

### Running quality checks

```bash
# Format code
ruff format .

# Lint code
ruff check . --fix

# Type checking
mypy optiride

# Run all pre-commit hooks
pre-commit run --all-files
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick contribution checklist

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run quality checks (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Cycling power model based on [Martin et al. (1998)](https://journals.humankinetics.com/view/journals/jab/14/3/article-p276.xml)
- Weather data from [Open-Meteo](https://open-meteo.com/)
- Nutrition guidelines based on [Jeukendrup (2014)](https://link.springer.com/article/10.1007/s40279-013-0079-0)

## 📮 Contact

**Romain BERTHET** - berthet.romain3@gmail.com

Project Link: [https://github.com/romainberthet/optiride](https://github.com/romainberthet/optiride)

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

</div>
