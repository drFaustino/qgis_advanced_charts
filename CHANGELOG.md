# Changelog
All notable changes to the **Advanced Charts** plugin are documented in this file.

This project follows the principles of [Semantic Versioning](https://semver.org/).

---

## [1.0.0] – 2026‑04‑07
### Added
- First public release of the plugin.
- Support for the following chart types:
  - Line
  - Scatter
  - Bar
  - Histogram
  - Pie
  - Boxplot
  - Area
  - Violin
  - Radar
- Multi‑series plotting (multiple Y fields).
- Subplot support (one subplot per Y field).
- Dual‑axis charts (primary Y + secondary Y2).
- Linear regression with automatic normalization and date handling.
- Curve fitting models:
  - Polynomial (configurable degree)
  - Exponential
  - Logarithmic
  - Power
- Selection‑based filtering (“Use selected features only”).
- Automatic chart type suggestion based on field types.
- Histogram bin suggestion system with warnings for oversampling/undersampling.
- Full styling customization:
  - Colors (Y, Y2, background)
  - Markers
  - Line styles
  - Grid
  - Legend
- Customizable titles (chart title, X axis, Y axis, Y2 axis).
- Export charts to PNG, JPG, and PDF.
- Modern, responsive UI built for Qt6 and QGIS 4.
- Matplotlib backend integration using QtAgg.

### Improved
- Completely reorganized UI layout for clarity and usability.
- Robust field type detection (numeric, date/time, string).
- Automatic conversion of date fields to ordinal values for regression and fitting.
- Clearer and fully translatable warning messages (TS‑ready).
- Full compatibility with QGIS 4 and Python 3.12.

### Fixed
- Corrected color widget rendering by switching to `QgsColorButton`.
- Removed duplicate widgets in the Style section.
- Fixed `.ui` loading issues under Qt6.
- Corrected subplot handling for chart types that do not support multiple axes (Pie, Boxplot).

---

## [Unreleased]
### Planned
- Save/load style presets.
- Built‑in chart themes (light/dark).
- 3D chart support (surface, 3D scatter).
- Interactive tooltips (hover) using Matplotlib.
- Integration with the QGIS Processing Toolbox.
- Print Layout export support.

---
