# Advanced Charts for QGIS 4

An advanced charting and visualization plugin for QGIS 4 + Qt6, powered by Matplotlib.

Advanced Charts allows you to generate high-quality charts directly from QGIS vector layers, including multi-series plots, subplots, histograms, pie charts, boxplots, violin plots, radar charts, regression analysis, curve fitting, area charts, and dual-axis (Y2) charts.

The plugin provides a clean and responsive interface with extensive customization options for colors, markers, line styles, axes, titles, legends, grids, and chart layout.

## ✨ Features
- Line charts
- Scatter charts
- Bar charts
- Histograms
- Pie charts
- Boxplots
- Area charts
- Violin plots
- Radar charts
- Linear regression
- Curve fitting
- Multi-series plotting
- One subplot per Y field
- Dual-axis charts (Y + Y2)
- Selection-based filtering
- Automatic chart type suggestion
- Histogram bin suggestions
- Customizable colors
- Customizable markers
- Customizable line styles
- Customizable chart and axis titles
- Grid and legend controls
- PNG, JPG, and PDF export
- Layer reload directly from the plugin interface
- Progress indicator during chart generation
- Automatic progress reset after chart generation
- Clear chart functionality preserving the original plot dimensions
- Date/time field support
- Automatic conversion of date values for numerical analysis
- Qt6-compatible Matplotlib integration
- Designed specifically for QGIS 4

## 🖥 User Interface Overview

The Advanced Charts dialog is divided into a data configuration panel on the left and the chart preview area on the right.

The interface is designed to remain usable when the available screen size is limited, while allowing the chart preview to preserve its original dimensions.

1. Data Section

### Layer

Select the QGIS vector layer from which the chart will be generated.

The layer list contains the layers currently available in the QGIS project.

### Reload

The Reload button refreshes the layer list from the current QGIS project.

This is useful when:

- a new layer has been added to the project;
- a layer has been removed;
- a layer has been renamed;
- the project contents have changed after opening the Advanced Charts dialog.

Reloading the layer list also refreshes the available fields for the selected layer.

### X Field

Select the field used for the X-axis.

Supported field types include:

- numeric fields;
- date fields;
- datetime fields;
- time fields;
- string fields.

String fields are particularly useful for categorical charts such as bar and pie charts.

Date and datetime fields are automatically converted to Matplotlib date values when required.

### Y Fields (multi-selection)

Select one or more fields to use as Y-axis series.

Multiple fields can be selected simultaneously.

Hold Ctrl to select individual fields.
Use Shift to select ranges of fields.
Each selected field becomes a separate data series.
If Separate subplot for each Y is enabled, each Y field is displayed in its own subplot.
Use selected features only

When enabled, only the currently selected features of the chosen QGIS layer are used.

This is useful for:

- analyzing a subset of features;
- comparing selected areas;
- creating charts from manually selected records;
- working with a filtered subset of the dataset.

If the option is enabled but no features are selected, the plugin displays a warning instead of generating an empty chart.

### Enable Y2 axis

Enables a secondary Y-axis on the right side of the chart.

Y2 is supported for:

- Line;
- Scatter;
- Linear Regression;
- Curve Fitting.

The secondary axis is useful when two variables have significantly different numerical scales.

For example, a chart can display:

- temperature on the primary Y-axis;
- precipitation on the secondary Y2-axis.

2. Chart Type Section

### Chart Type

The plugin supports the following chart types:

- Line
- Scatter
- Bar
- Histogram
- Pie
- Boxplot
- Area
- Violin
- Radar
- Linear Regression
- Curve Fitting
- Suggest chart type automatically

When enabled, Advanced Charts analyzes the X and Y field types and automatically suggests a suitable chart type.

The current logic includes:

- X = string + numeric Y → Bar
- X = date + numeric Y → Line
- X = numeric + numeric Y → Scatter
- Other combinations → Histogram

The suggested type can always be manually overridden.

### Separate subplot for each Y

Creates a separate subplot for each selected Y field.

This is useful when:

- different Y fields have very different scales;
- several series overlap excessively;
- individual trends need to be examined independently.

Separate subplots are not recommended for:

- Pie charts;
- Boxplots;
- Bar charts.

The plugin displays an informational message when these combinations are selected.

### Bins (histogram)

Controls the number of bins used by histogram charts.

Advanced Charts also provides an automatic bin recommendation based on the data distribution.

The plugin warns the user when:

- the selected number of bins is excessively high;
- the selected number of bins is excessively low.

This helps avoid noisy or oversimplified histograms.

3. Style Section

The Style section provides controls for customizing the visual appearance of generated charts.

### Y Color

Sets the primary color used by the Y series.

When multiple Y fields are selected, the first series uses the selected Y color while additional series use the Matplotlib color cycle.

### Background

Sets the background color of the plotting area.

### Y Marker

Controls the marker used by the primary Y series.

Available marker styles include:

- None
- Circle
- X
- Square
- Triangle
- Diamond
- Star
- Plus
- Vertical line
- Horizontal line
- and other Matplotlib markers.

### Y Line Style

Controls the line style used by the primary Y series.

Available styles include:

- None
- Solid
- Dashed
- Dash-dot
- Dotted
- Y2 Color

Sets the color of the secondary Y2 series.

The default Y2 color is red.

### Y2 Marker

Controls the marker used by the Y2 series.

### Y2 Line Style

Controls the line style used by the Y2 series.

### Grid

Enables or disables the chart grid.

### Legend

Enables or disables the chart legend.

The legend automatically combines information from:

- primary Y series;
- secondary Y2 series;
- regression lines;
- curve-fitting lines.

4. Regression and Curve Fitting

The Regression and Curve Fitting section provides statistical analysis tools.

### Polynomial degree

Controls the polynomial degree used by polynomial curve fitting.

Supported values range from:

1 to 10

The default value is 2.

### Fit Type

The plugin supports the following curve-fitting models:

- Polynomial
- Exponential
- Logarithmic
- Power

Polynomial fitting uses NumPy.

The other fitting models use SciPy when available.

### Enable linear regression

Adds a linear regression line to the chart.

The regression implementation supports:

- numeric X values;
- date X values;
- numeric Y values;
- automatic date conversion;
- X normalization to avoid numerical overflow.

The regression line is displayed using a dashed line.

5. Titles Section

The Titles section allows the user to customize all major chart labels.

### Chart title

Sets the main chart title.

If no custom title is entered, the plugin automatically generates a title based on the chart type and selected layer.

### X axis title

Sets the title of the X-axis.

If empty, the selected X field name is used.

### Y axis title

Sets the title of the primary Y-axis.

If empty, the default label is used.

### Y2 axis title

Sets the title of the secondary Y2-axis.

This control is enabled only when the Y2 axis option is active.

If no title is entered, the selected Y2 field name is used.

6. Chart Preview

The chart preview is displayed on the right side of the dialog.

The Matplotlib canvas is embedded directly into the QGIS interface using the QtAgg backend.

The chart area is designed to preserve its original layout dimensions when the chart is cleared.

This prevents the preview from becoming progressively smaller or compressed after repeated use of the Clear chart button.

The chart also uses Matplotlib's layout management to reduce clipping of:

- titles;
- axis labels;
- tick labels;
- legends;
- chart contents.

Date axes automatically use Matplotlib date formatting and automatic date locators.

7. Progress Indicator

The plugin includes a progress bar and status label below the main controls.

During chart generation, the progress indicator provides visual feedback that the operation is being processed.

After the chart has been successfully generated, the progress bar is automatically returned to:

0%

This ensures that the progress indicator is ready for the next chart generation operation.

8. Buttons

### Reload

Reloads the layer list from the current QGIS project.

It can be used after adding, removing, or changing layers while the Advanced Charts dialog is open.

### Chart

Generates the chart using the currently selected:

- layer;
- X field;
- Y fields;
- chart type;
- styling options;
- regression/fitting options;
- Y2 configuration.
- Save image


## 📦 Installation

### Windows

Copy the plugin folder into:

%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\


For example:

%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\qgis_advanced_charts\

### Linux

Copy the plugin folder into:

~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/


Then:

Restart QGIS.
Open Plugins → Manage and Install Plugins.
Enable Advanced Charts.

## 🧪 Compatibility

Advanced Charts is designed for:

QGIS 4.x
Qt 6.x
Python 3.12
Matplotlib
QtAgg Matplotlib backend

The plugin is designed specifically for the QGIS 4 / Qt6 API.

SciPy

SciPy is optional.

It is required for:

- Exponential curve fitting;
- Logarithmic curve fitting;
- Power curve fitting.

Polynomial fitting uses NumPy and does not require SciPy.


## 🧑 ‍Author

Dr. Geol. Faustino Cetraro

Repository:

https://github.com/drFaustino/qgis_advanced_charts

📝 License

MIT License

🗺️ Roadmap

Planned features include:

Save/load style presets
Built-in chart themes
Light/dark themes
3D surface charts
3D scatter plots
Interactive hover tooltips
QGIS Processing Toolbox integration
Print Layout export
Additional statistical analysis tools
Additional chart customization options
📋 Changelog

See CHANGELOG.md for the complete project history.

Current version:

1.2.0

## 🤝 Contributing

Bug reports, feature requests, and contributions are welcome.

Please use the project's GitHub repository to report issues or propose improvements.

⭐ Advanced Charts

Advanced Charts brings statistical visualization and chart generation directly into QGIS 4, combining the QGIS data model with the flexibility and power of Matplotlib.

## Interface

<img width="1374" height="993" alt="img6" src="https://github.com/user-attachments/assets/8314f7f4-af7f-4a2c-9a68-086bfbc4b558" />
