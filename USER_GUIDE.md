📘 Advanced Charts – Full User Guide
Advanced Charts is a powerful visualization plugin for QGIS 4 + Qt6, designed to generate high‑quality charts directly from vector layer attributes.
It supports multi‑series plotting, subplots, dual‑axis charts, regression, curve fitting, and extensive styling options.

This guide explains how to use every feature, from basic charts to advanced analytical workflows.

1. Introduction
Advanced Charts allows you to:

Explore attribute data visually

Compare multiple variables

Analyze trends, distributions, and relationships

Export publication‑quality charts

Perform regression and curve fitting

Create multi‑series and multi‑subplot visualizations

Charts are generated using Matplotlib (QtAgg backend) and displayed directly inside QGIS.

2. Opening the Plugin
Load a vector layer in QGIS.

Go to Plugins → Advanced Charts → Open Chart Dialog.

The interface opens with:

Left panel: all chart options

Right panel: the chart preview

3. Data Section
This section defines what data will be plotted.

3.1 Layer
Select the vector layer containing the attributes you want to visualize.

Only layers with attribute fields appear in the list.

3.2 X Field
Choose the field for the X‑axis.

Supported types:

Numeric → scatter, line, regression

Date/Time → time series

String → bar, pie

3.3 Y Fields (multi‑selection)
Select one or more fields to plot on the Y‑axis.

How to select multiple:

Ctrl + click to add/remove fields

Each selected field becomes a separate series

Use cases:

Compare multiple numeric variables

Plot multiple time series

Create multi‑subplot dashboards

3.4 Use selected features only
If enabled, the chart uses only the selected features of the layer.

Useful for:

analyzing a specific region

comparing subsets

filtering outliers

If no features are selected, the plugin warns you.

3.5 Enable Y2 axis
Adds a secondary Y‑axis on the right side.

Use Y2 when:

two variables have different scales

you want to compare trends without overlap

Supported chart types:

Line

Scatter

Linear Regression

Curve Fitting

4. Chart Type Section
This section defines the type and structure of the chart.

4.1 Chart type
Available chart types:

Basic charts
Line

Scatter

Bar

Histogram

Pie

Boxplot

Area

Advanced charts
Violin

Radar

Linear Regression

Curve Fitting

4.2 Suggest chart type automatically
When enabled, the plugin analyzes the data and suggests the most appropriate chart.

Rules:

X = string → Bar

X = date → Line

X = numeric → Scatter

Otherwise → Histogram

You can override the suggestion manually.

4.3 Separate subplot for each Y
Creates one subplot per Y field.

Recommended when:

Y fields have different scales

you want to compare shapes rather than values

Not recommended for:

Pie

Boxplot

Bar

4.4 Bins (histogram)
Number of bins for histogram charts.

The plugin includes a bin suggestion system:

warns if bins are too many (noisy chart)

warns if bins are too few (oversimplified chart)

5. Style Section
Customize the appearance of the chart.

5.1 Y Color
Color of the primary Y series.

5.2 Background
Background color of the plot area.

5.3 Y Marker / Y Line Style
Marker and line style for the Y series.

5.4 Y2 Color / Marker / Line Style
Same options for the secondary Y2 axis.

5.5 Grid
Enable/disable grid lines.

5.6 Legend
Show/hide the legend.

6. Regression and Curve Fitting
This section provides analytical tools for trend analysis.

6.1 Polynomial degree
Used when “Polynomial” is selected.

6.2 Fit type
Available models:

Polynomial

Exponential

Logarithmic

Power

6.3 Enable linear regression
Adds a regression line to the chart.

The plugin automatically:

converts dates to ordinal numbers

normalizes values

draws a clean regression line

Works with:

Line

Scatter

Curve Fitting

7. Titles Section
Customize chart labels.

Chart title

X axis title

Y axis title

Y2 axis title

If left empty, defaults are used.

8. Buttons
Generate chart
Creates the chart.

Save image
Exports the chart as PNG, JPG, or PDF.

Clear chart
Resets the plot area.

Close
Closes the dialog.

9. Advanced Examples
Below are complete workflows demonstrating advanced usage.

Example 1 — Multi‑Series Line Chart (Time Series)
Goal: Compare temperature, humidity, and pressure over time.

Steps:
Layer: weather_stations

X Field: date

Y Fields: select:

temperature

humidity

pressure

Chart type: Line

Enable:

Grid

Legend

Titles:

Chart: Weather Trends

X: Date

Y: Values

Generate chart

Result:  
A multi‑series time‑series line chart.

Example 2 — Dual‑Axis Chart (Y + Y2)
Goal: Compare population growth (Y) and GDP (Y2).

Steps:
X Field: year

Y Fields: population

Enable Y2 axis

Y2 Field: gdp

Chart type: Line

Customize colors:

Y: blue

Y2: red

Generate chart

Result:  
Population and GDP plotted together with separate scales.

Example 3 — Histogram with Optimal Bins
Goal: Analyze distribution of building heights.

Steps:
X Field: (ignored)

Y Fields: height

Chart type: Histogram

Bins: start with 10

If warning appears, adjust bins accordingly

Generate chart

Result:  
A clean histogram with optimal binning.

Example 4 — Boxplot for Statistical Comparison
Goal: Compare elevation across three regions.

Steps:
Y Fields:

elev_region_a

elev_region_b

elev_region_c

Chart type: Boxplot

Generate chart

Result:  
A boxplot comparing distributions across regions.

Example 5 — Curve Fitting (Polynomial)
Goal: Fit a polynomial curve to traffic volume.

Steps:
X Field: hour

Y Fields: traffic_volume

Chart type: Curve Fitting

Fit type: Polynomial

Degree: 3

Enable linear regression (optional)

Generate chart

Result:  
A polynomial curve showing traffic patterns.

Example 6 — Radar Chart (Category Comparison)
Goal: Compare average values of multiple indicators.

Steps:
Y Fields:

indicator_a

indicator_b

indicator_c

indicator_d

Chart type: Radar

Generate chart

Result:  
A radar chart showing category averages.

10. Best Practices
Use multi‑selection to compare variables quickly.

Use Y2 axis when scales differ significantly.

Use subplots when comparing shapes rather than values.

Use histograms for distributions and boxplots for statistical comparison.

Use regression to identify trends.

Use curve fitting to model complex relationships.

Always check field types before choosing a chart.

11. Troubleshooting
Chart is empty
Check that X and Y fields contain valid data.

Ensure selected features exist if filtering is enabled.

Regression line not visible
Ensure X is numeric or date.

Ensure Y contains numeric values.

Pie chart not working
Only one Y field is allowed.

Subplots not working
Not supported for Pie, Boxplot, Bar.

12. Credits
Developed by Dr. Geol. Faustino Cetraro  