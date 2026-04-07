# Advanced Charts for QGIS 4  
An advanced charting and visualization plugin for QGIS 4 + Qt6, powered by Matplotlib.

Advanced Charts allows you to generate high‑quality plots directly from vector layers, including multi‑series charts, subplots, histograms, pie charts, boxplots, violin plots, radar charts, regressions, curve fitting, and dual‑axis (Y2) charts.  
The plugin is designed with a clean, responsive UI and supports full customization of styles, colors, markers, and axes.

---

## ✨ Features

- Line, Scatter, Bar, Histogram, Pie, Boxplot, Area, Violin, and Radar charts  
- Multi‑series plotting (multiple Y fields)  
- Subplots (one chart per Y field)  
- Dual‑axis charts (Y + Y2)  
- Linear regression  
- Curve fitting (Polynomial, Exponential, Logarithmic, Power)  
- Selection‑based filtering  
- Automatic chart type suggestion  
- Customizable colors, markers, line styles  
- Export charts as PNG, JPG, or PDF  
- Fully compatible with QGIS 4 and Qt6  

---

# 🖥️ User Interface Overview

Below is a detailed explanation of each section and option in the plugin.

---

# 1. **Data Section**

### **Layer**
Select the vector layer from which the chart will be generated.

### **X Field**
The field used for the X‑axis.  
Supports:
- numeric fields  
- date/time fields  
- string fields (for bar/pie charts)

### **Y Fields (multi‑selection)**
Select one or more fields to plot on the Y‑axis.

- Hold **Ctrl** to select multiple fields  
- Each selected field becomes a separate series  
- If “Separate subplot for each Y” is enabled, each field gets its own subplot  

### **Use selected features only**
If enabled, the chart uses **only the selected features** of the layer.

Useful for:
- focusing on a subset  
- comparing specific regions  
- analyzing filtered data  

If no features are selected, the plugin warns the user.

### **Enable Y2 axis**
Adds a **secondary Y‑axis** on the right side of the chart.

Supported chart types:
- Line  
- Scatter  
- Linear Regression  
- Curve Fitting  

Y2 is ideal when:
- two series have very different scales  
- you want to compare trends without overlapping  

---

# 2. **Chart Type Section**

### **Chart type**
Choose the type of chart to generate:

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

### **Suggest chart type automatically**
When enabled, the plugin analyzes the data types and suggests the most appropriate chart:

- X = string → Bar  
- X = date → Line  
- X = numeric → Scatter  
- Otherwise → Histogram  

You can override the suggestion manually.

### **Separate subplot for each Y**
Creates one subplot per Y field.

Recommended when:
- Y fields have different scales  
- you want to compare shapes rather than values  

Not recommended for:
- Pie  
- Boxplot  
- Bar  

### **Bins (histogram)**
Number of bins for histogram charts.

The plugin also includes a **bin suggestion system** that warns you if:
- bins are too many (chart becomes noisy)  
- bins are too few (chart becomes oversimplified)  

---

# 3. **Style Section**

### **Y Color**
Color of the primary Y series.

### **Background**
Background color of the plot area.

### **Y Marker**
Marker style for Y series (scatter/line).

### **Y Line Style**
Line style for Y series.

### **Y2 Color**
Color of the secondary Y2 series.

### **Y2 Marker**
Marker style for Y2 series.

### **Y2 Line Style**
Line style for Y2 series.

### **Grid**
Enable/disable grid lines.

### **Legend**
Show/hide the legend.

---

# 4. **Regression and Curve Fitting**

### **Polynomial degree**
Degree of the polynomial used when “Polynomial” is selected.

### **Fit type**
Choose the curve fitting model:

- Polynomial  
- Exponential  
- Logarithmic  
- Power  

### **Enable linear regression**
Adds a linear regression line to the chart.

Works with:
- Line  
- Scatter  
- Curve Fitting  

Regression is computed using:
- automatic conversion of dates to ordinal numbers  
- normalization to avoid overflow  
- robust fitting for all numeric X/Y combinations  

---

# 5. **Titles Section**

### **Chart title**
Main title displayed above the chart.

### **X axis title**
Label for the X‑axis.

### **Y axis title**
Label for the primary Y‑axis.

### **Y2 axis title**
Label for the secondary Y2 axis (if enabled).

---

# 6. **Buttons**

### **Generate chart**
Creates the chart based on the selected options.

### **Save image**
Exports the chart as:
- PNG  
- JPG  
- PDF  

### **Clear chart**
Resets the plot area to an empty chart.

### **Close**
Closes the dialog.

---

# 📦 Installation

1. Download or clone the repository  
2. Copy the plugin folder into:  
   - **Windows:** `%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\`  
   - **Linux:** `~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/`  
3. Restart QGIS  
4. Enable *Advanced Charts* from **Plugins → Manage and Install Plugins**

---

# 🧪 Compatibility

- QGIS **4.0+**  
- Qt **6.x**  
- Python **3.12**  
- Matplotlib backend (QtAgg)  

SciPy is optional (required only for non‑polynomial curve fitting).

---

# 🧑‍💻 Author

**Dr. Geol. Faustino Cetraro**  

---

# 📝 License

MIT License

---

# 🧭 Roadmap

- Export chart presets  
- Theming system (dark/light)  
- 3D charts  
- Interactive charts (hover tooltips)  
- Processing toolbox integration  
