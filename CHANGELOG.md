# Changelog

All notable changes to the Advanced Charts plugin are documented in this file.

This project follows the principles of Semantic Versioning
.

## 1.2.0 – 2026-08-30
### Added
- Added a Reload button next to the Layer selector.
- Added the ability to refresh the project layer list without reopening the dialog.
- Added progress feedback during chart generation.
- Added automatic progress bar reset to 0% after chart generation.
- Improved status feedback during chart processing.
- Improved
- Improved layer and field refresh handling.
- Improved Matplotlib canvas management.
- Improved chart area sizing and layout behavior.
- Preserved the original plot area dimensions when clearing the chart.
- Prevented the chart from being vertically compressed after clearing or regenerating a plot.
- Improved plot rendering inside the groupBoxPlot.
- Improved handling of the Matplotlib canvas when replacing or clearing figures.
- Improved chart layout to reduce clipping on the left and bottom edges.
- Improved compatibility between Matplotlib, Qt6 and QGIS 4.
- Improved Qt6 cursor handling.
- Removed obsolete pass statements from the Python implementation.
- Improved code organization and error handling.
- Improved UI responsiveness during chart generation and reset operations.

###Fixed
- Fixed NameError: name 'Qt' is not defined caused by incorrect Qt cursor handling.
- Fixed chart clipping on the left side of the plot area.
- Fixed chart height being reduced after clearing or regenerating the plot.
- Fixed plot area resizing when using the Clear chart button.
- Fixed progress bar remaining at its previous value after chart generation.
- Fixed canvas replacement behavior when clearing the chart.
- Fixed Y2 data conversion order in the chart generation workflow.
- Fixed potential references to Y2 data before initialization.
- Fixed chart reset behavior so that the plot retains the original dialog layout dimensions.

## 1.1.0 – 2026-04-07
### Added
First public release of the plugin.
Support for the following chart types:
- Line
- Scatter
- Bar
- Histogram
- Pie
- Boxplot
- Area
- Violin
- Radar
- Multi-series plotting using multiple Y fields.
- Subplot support with one subplot per Y field.
- Dual-axis charts using primary Y and secondary Y2 axes.
- Linear regression with automatic normalization and date handling.
- Curve fitting models:
- Polynomial with configurable degree
- Exponential
- Logarithmic
- Power
- Selection-based filtering using Use selected features only.
- Automatic chart type suggestion based on field types.
- Histogram bin suggestion system with warnings for oversampling and undersampling.
- Full styling customization:
- Y color
- Y2 color
- Background color
- Markers
- Y2 markers
- Line styles
- Y2 line styles
- Grid
- Legend
 - Customizable chart titles.
 - Customizable X-axis, Y-axis and Y2-axis titles.
- Export charts to PNG, JPG and PDF.
- Modern responsive UI built for Qt6 and QGIS 4.
- Matplotlib integration using the QtAgg backend.

### Improved
- Completely reorganized UI layout for clarity and usability.
- Robust field type detection for numeric, date/time and string fields.
- Automatic conversion of date fields to Matplotlib date values.
- Automatic date handling for regression and curve fitting.
- Clearer and fully translatable warning messages.
- Improved compatibility with QGIS 4 and Python 3.12.
- Improved handling of multiple Y series.
- Improved support for date-based X axes.
- Improved dual Y-axis visualization.

### Fixed
- Corrected color widget rendering by switching to QgsColorButton.
- Removed duplicate widgets in the Style section.
- Fixed .ui loading issues under Qt6.
- Corrected subplot handling for chart types that do not support multiple axes.
- Corrected handling of Pie and Boxplot charts with multiple Y fields.
- Fixed date conversion issues affecting Matplotlib charts.
- Fixed several chart rendering and styling issues.
