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

### ⚡ Simplified interface - Just GPX + Rider info!

OptiRide now includes a **comprehensive bike database** with **automatic CdA adjustment** based on your height and weight!

**Minimum required:**
- Your GPX trace
- Your weight and FTP
- Target power on flat

**Optional but recommended:**
- Your height (for precise CdA estimation)
- Bike type (defaults to `aero_road`)

```bash
# Basic usage - CdA automatically adjusted for your size!
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 \
  --height 1.80 \
  --ftp 260 \
  --power-flat 220
```

### 🚴 Choose your bike and position

```bash
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 --height 1.80 --ftp 260 \
  --bike-type aero_road \
  --position drops \
  --wheels deep_section \
  --power-flat 220
```

**Available bike types:**
- `road_race` - Lightweight racing bike (7.5kg, CdA 0.08)
- `aero_road` - Aerodynamic road bike (8.2kg, CdA 0.07) ⚡ **Default**
- `time_trial` - TT/Tri bike (9.0kg, CdA 0.06)
- `gravel` - Gravel/all-road bike (9.5kg, CdA 0.10)
- `mountain` - XC mountain bike (11.0kg, CdA 0.12)
- `road_endurance` - Comfort road bike (8.5kg, CdA 0.09)

**Available positions:**
- `upright` - Hands on hoods, relaxed (CdA +0.35)
- `drops` - Hands in drops (CdA +0.28) ⚡ **Default**
- `aero_hoods` - Elbows tucked (CdA +0.30)
- `time_trial` - On aerobars (CdA +0.22)
- `super_tuck` - Extreme aero/descending (CdA +0.18)

### With automatic weather

```bash
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 --ftp 260 \
  --power-flat 220 \
  --auto-weather --hour 9
```

### 🗺️ Export interactive map

Generate a beautiful interactive HTML map with power zones visualization:

```bash
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 --height 1.80 --ftp 260 \
  --power-flat 220 \
  --export-map
```

**Features of the interactive map:**
- 🎨 Color-coded route by power zones
- 📊 Elevation profile chart
- 📈 Ride statistics panel
- 🔍 Click on segments for detailed info
- 🗺️ Multiple map layers (terrain, satellite, etc.)
- 📱 Responsive design works on mobile

**Installation required:**
```bash
pip install "optiride[maps]"
# or
pip install folium
```

### Optimize start time

Find the best time to start based on weather conditions:

```bash
optiride optimize-start \
  --gpx examples/sample.gpx \
  --mass 72 --ftp 260 \
  --power-flat 220 \
  --start-hour 6 --end-hour 20 \
  --export-gpx
```

### Advanced: Manual configuration override

For experienced users who want precise control:

```bash
optiride compute \
  --gpx examples/sample.gpx \
  --mass 72 --ftp 260 \
  --bike-type aero_road \
  --cda 0.285 \
  --crr 0.0032 \
  --bike-mass 7.8 \
  --power-flat 220
```

### Output files

- `outputs/summary.json`: Comprehensive ride summary (time, kCal, nutrition plan)
- `outputs/targets.csv`: Detailed point-by-point targets (distance, slope, power, speed)
- `outputs/plots/*.png`: Elevation profile, power curve, speed profile
- `outputs/power_targets.gpx`: GPX file with power extensions (optional, `--export-gpx`)
- `outputs/interactive_map.html`: Interactive map with power zones (optional, `--export-map`) 🆕

## 🐍 Python API

### Quick start with bike library

```python
import optiride as opr
from optiride.bike_library import get_bike_config

# Get complete bike configuration from library
# CdA is automatically adjusted for rider size!
bike_config = get_bike_config(
    bike_type="aero_road",
    position="drops",
    wheels="deep_section",
    rider_height_m=1.80,  # Your height
    rider_mass_kg=72.0    # Your weight
)
# Returns: {'mass_kg': 8.1, 'cda': 0.346, 'crr': 0.0032, 'drivetrain_efficiency': 0.977}
# CdA is scaled based on your anthropometry!

# Create rider with library values
rider = opr.RiderBike(
    mass_rider_kg=72.0,
    mass_bike_kg=bike_config["mass_kg"],
    cda=bike_config["cda"],  # Already adjusted for your size
    crr=bike_config["crr"],
    drivetrain_eff=bike_config["drivetrain_efficiency"],
    ftp=260.0,
    w_prime_j=20000.0
)

# Set environment
env = opr.Environment(
    air_density=1.225,
    wind_u_ms=0.0,  # East wind (m/s)
    wind_v_ms=0.0   # North wind (m/s)
)

# Calculate required power for given speed
power = opr.power_required(
    v_ms=10.0,       # 36 km/h
    slope_tan=0.05,  # 5% grade
    bearing_deg=0.0, # Heading north
    rb=rider,
    env=env
)

print(f"Required power: {power:.1f} W")

# Example: Compare CdA for different rider sizes
small_rider = get_bike_config("aero_road", "drops", rider_height_m=1.65, rider_mass_kg=60.0)
large_rider = get_bike_config("aero_road", "drops", rider_height_m=1.95, rider_mass_kg=90.0)
print(f"Small rider CdA: {small_rider['cda']:.3f}")  # ~0.31
print(f"Large rider CdA: {large_rider['cda']:.3f}")  # ~0.37
```

### Manual configuration (advanced)

```python
import optiride as opr

# Define rider and bike manually
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

#### Essential Parameters (Required)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--gpx` | Path to GPX file | `route.gpx` |
| `--mass` | Rider weight (kg) | `72` |
| `--ftp` | Functional Threshold Power (W) | `260` |
| `--power-flat` | Target power on flat terrain (W) | `220` |

#### Rider Anthropometry (Optional but recommended)

| Parameter | Description | Effect |
|-----------|-------------|--------|
| `--height` | Rider height in meters | Automatically adjusts CdA for your size |

**How it works:** If you provide your height, OptiRide uses the DuBois formula to estimate your frontal area and scale the CdA accordingly. A taller/larger rider will have a proportionally higher CdA, while a smaller rider will have a lower CdA. This provides much more accurate predictions than using generic reference values!

#### Bike Configuration (Optional - uses library defaults)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--bike-type` | Bike category (see list above) | `aero_road` |
| `--position` | Riding position (see list above) | `drops` |
| `--wheels` | Wheel type | `mid_depth` |

**Tip:** The bike library automatically configures mass, CdA, Crr, and efficiency based on your bike type!

#### Advanced Manual Overrides (Optional)

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `--bike-mass` | Override bike weight (kg) | 6-10 |
| `--cda` | Override drag area (m²) | 0.20-0.40 |
| `--crr` | Override rolling resistance | 0.002-0.005 |
| `--eff` | Override drivetrain efficiency | 0.95-0.98 |
| `--wprime` | Anaerobic capacity W' (J) | 15000-25000 |
| `--cp` | Critical Power (W) | 250-350 |
| `--age` | Rider age for HR calculations | 20-60 |

#### Pacing Strategy

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--up-mult` | Power multiplier for climbs | 1.10 |
| `--down-mult` | Power multiplier for descents | 0.75 |
| `--max-delta` | Max power change between points (W) | 30.0 |
| `--step-m` | Resampling distance (m) | 20.0 |

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
