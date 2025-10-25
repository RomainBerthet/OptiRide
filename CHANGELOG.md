# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-25

### 🎉 Initial Release

OptiRide v0.1.0 is a professional cycling pacing optimizer that combines physics-based modeling, physiological constraints, and real-time weather data to generate optimal power targets and nutrition plans.

### ✨ Core Features

#### Physics & Power Modeling
- **GPX file parsing and resampling** with configurable step distance
- **Physics-based power calculations** using validated Martin et al. (1998) model
- **Pacing optimization** with terrain-adaptive power targets
- **Critical Power (CP) and W' balance modeling** for fatigue tracking (Skiba et al. 2012)
- **Wind impact analysis** with bearing-aware aerodynamic calculations

#### Bike & Rider Configuration
- **Comprehensive bike database** with 6 bike types (road racing, aero road, time trial, gravel, mountain, endurance)
- **5 riding positions** (upright, drops, aero hoods, time trial, super tuck)
- **5 wheel configurations** (shallow alloy, shallow carbon, mid-depth, deep section, disc rear)
- **Anthropometric CdA scaling** using DuBois formula for personalized aerodynamic estimates
- **Automatic configuration** - only GPX trace, weight, and FTP required

#### Power & Pacing Intelligence
- **Personalized FTP-based power zones** using Coggan 7-zone model
- **Auto-calculated target power** from FTP with duration-aware intensity (92%/87%/80%/70% for different ride lengths)
- **Intensity factor option** for explicit power control (0.0-1.0 × FTP)
- **Backward compatibility** with explicit `--power-flat` parameter

#### Nutrition & Fueling
- **Smart refueling recommendations** based on scientific guidelines (Jeukendrup 2014)
- **W' balance tracking** for real-time fatigue estimation
- **Adaptive nutrition type selection** (gels, bars, drinks, solids) based on:
  - Current fatigue level
  - Ride intensity
  - Time elapsed
- **Detailed fueling points** with carbohydrates (g), fluids (ml), sodium (mg), energy deficit (kcal)
- **Multi-factor fatigue index** (W' depletion, duration, intensity)

#### Weather Integration
- **Automatic weather fetching** via Open-Meteo API (no API key required)
- **Real-time meteorological data**: temperature, humidity, pressure, wind
- **Wind projection** onto route bearing for accurate aerodynamic drag
- **Start time optimization** to find best weather window (6-20h scan)

#### Visualizations & Exports
- **Interactive HTML maps** with Folium/Leaflet.js:
  - Color-coded route by personalized FTP power zones
  - Smart refueling markers with detailed popups
  - Elevation profile chart
  - Ride statistics panel
  - Multiple map layers (OpenStreetMap, OpenTopoMap, CartoDB)
  - Mobile-responsive design
- **Static plots**: elevation profile, power targets, speed estimates
- **Multiple export formats**:
  - CSV: Point-by-point targets (distance, slope, power, speed)
  - GPX: Power extensions compatible with cycling computers
  - JSON: Comprehensive ride summary with nutrition plan
  - HTML: Interactive map with refueling points

### 🛠️ Technical Excellence

#### Code Quality
- **Type-safe codebase** with comprehensive type hints (MyPy strict mode)
- **Google-style docstrings** for all public APIs
- **Modern Python tooling**:
  - Ruff for linting and formatting
  - MyPy for static type checking
  - Pytest with 78 tests and 97% coverage on core modules
  - Pre-commit hooks for automated quality checks
- **Python 3.9+ support** with backward-compatible type annotations

#### Developer Experience
- **Professional documentation**:
  - Comprehensive README with examples
  - Parameter guide with typical ranges
  - Scientific references and acknowledgments
  - CONTRIBUTING.md and CODE_OF_CONDUCT.md
- **Clean CLI interface** with helper functions and minimal required parameters
- **Flexible API** for programmatic use
- **Extensive test suite** with unit and integration tests

### 📚 Scientific References

This release implements models and guidelines from peer-reviewed research:

- **Martin et al. (1998)** - Cycling power equation validation
- **Skiba et al. (2012)** - W' balance differential model
- **Coggan (2003)** - FTP-based training zones
- **Jeukendrup (2014)** - Carbohydrate intake guidelines
- **Thomas et al. (2016)** - ACSM nutrition and hydration recommendations
- **DuBois & DuBois (1916)** - Body surface area formula for CdA scaling

### 🚀 Getting Started

#### Minimal Usage
```bash
optiride compute --gpx trace.gpx --mass 72 --ftp 260
```

#### With Interactive Map
```bash
optiride compute --gpx trace.gpx --mass 72 --height 1.80 --ftp 260 --export-map
```

#### Start Time Optimization
```bash
optiride optimize-start --gpx trace.gpx --mass 72 --ftp 260 --start-hour 6 --end-hour 20
```

### 📦 Installation

```bash
# Standard installation
pip install optiride

# With interactive maps
pip install "optiride[maps]"

# Development installation
pip install -e ".[dev,docs,jupyter,maps]"
```

### 🙏 Acknowledgments

Special thanks to the cycling science community and the open-source projects that made this possible:
- Open-Meteo for free weather API
- Folium for interactive mapping
- The Python scientific stack (NumPy, SciPy, Pandas, Matplotlib)

### 📄 License

This project is licensed under the MIT License.

---

**Full Changelog**: https://github.com/romainberthet/optiride/commits/v0.1.0

[0.1.0]: https://github.com/romainberthet/optiride/releases/tag/v0.1.0
