# chart_dialog.py  — Advanced Charts
# QGIS 4 + Qt6, Matplotlib backend, TS-ready (English)

import os
import datetime

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor

from qgis.core import QgsProject, QgsField

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "advanced_charts_dialog.ui")
)


class ChartDialog(QDialog, FORM_CLASS):

    def __init__(self, iface):
        super().__init__()
        self.setupUi(self)

        self.iface = iface

        # Matplotlib canvas
        self.canvas = FigureCanvas(plt.figure(constrained_layout=True))
        self.plotLayout.addWidget(self.canvas)

        # Initial UI state
        self._init_tooltips()
        self._init_style_controls()
        self._init_defaults()

        # Populate layers and fields
        self.populate_layers()

        # Connections
        self.layerCombo.currentIndexChanged.connect(self.populate_fields)
        self.plotButton.clicked.connect(self.plot)
        self.saveButton.clicked.connect(self.save_plot)
        self.chartTypeCombo.currentIndexChanged.connect(self.on_chart_type_changed)
        self.separateSubplotsCheck.stateChanged.connect(self.on_subplot_option_changed)
        self.enableY2Check.stateChanged.connect(self.toggle_y2_title)
        self.clearButton.clicked.connect(self.clear_plot)
        self.closeButton.clicked.connect(self.close)
        self.selectedOnlyCheck.stateChanged.connect(self.populate_fields)
        self.enableLinearRegressionCheck.setChecked(False)

        # Empty initial plot
        self.init_empty_plot()

    # ---------------------------------------------------------------------
    # UI INITIALIZATION
    # ---------------------------------------------------------------------

    def _init_tooltips(self):
        self.binSpin.setToolTip(
            self.tr(
                "Number of histogram bins.\n"
                "More bins = more detail.\n"
                "Fewer bins = simpler chart.\n"
                "Use high values only with large numeric datasets."
            )
        )
        self.selectedOnlyCheck.setToolTip(
            self.tr("Use only selected features from the chosen layer.")
        )
        self.enableY2Check.setToolTip(
            self.tr("Enable a secondary Y axis (Y2) for line or scatter charts.")
        )
        self.autoChartCheck.setToolTip(
            self.tr("Automatically suggest a chart type based on X and Y field types.")
        )
        self.separateSubplotsCheck.setToolTip(
            self.tr("Create a separate subplot for each Y field (not recommended for Pie/Boxplot).")
        )

    def _init_style_controls(self):
        # Markers
        markers = [
            "None", "o", "x", "s", "^", "v", "<", ">", "D", "d", "*", "+", "|", "_", "P", "X"
        ]
        # Line styles
        line_styles = ["None", "-", "--", "-.", ":"]

        self.markerCombo.addItems(markers)
        self.markerY2Combo.addItems(markers)

        self.lineStyleCombo.addItems(line_styles)
        self.lineStyleY2Combo.addItems(line_styles)

        # Colors (QgsColorWidget)
        self.colorWidgetY.setColor(QColor("#1f77b4"))   # Matplotlib blue
        self.colorWidgetY2.setColor(QColor("#d62728"))  # Matplotlib red
        self.colorWidgetBg.setColor(QColor("#ffffff"))  # White background

        # Y2 title enabled state
        self.y2AxisTitleEdit.setEnabled(self.enableY2Check.isChecked())

    def _init_defaults(self):
        self.binSpin.setValue(10)
        self.gridCheck.setChecked(True)
        self.legendCheck.setChecked(True)
        self.selectedOnlyCheck.setChecked(False)
        self.separateSubplotsCheck.setChecked(False)
        self.autoChartCheck.setChecked(True)

    # ---------------------------------------------------------------------
    # EMPTY / CLEAR PLOT
    # ---------------------------------------------------------------------

    def init_empty_plot(self):
        fig = plt.figure(constrained_layout=True)
        self.canvas.figure = fig
        fig.clear()

        ax = fig.add_subplot(111)
        ax.set_facecolor("#ffffff")
        ax.grid(True)

        ax.set_title(self.tr("Chart"), fontweight="bold", pad=20)
        ax.set_xlabel(self.tr("X axis"), fontweight="bold", labelpad=15)
        ax.set_ylabel(self.tr("Y axis"), fontweight="bold", labelpad=15)

        self.canvas.draw()

    def clear_plot(self):
        self.plotLayout.removeWidget(self.canvas)
        self.canvas.setParent(None)

        self.canvas = FigureCanvas(plt.figure(constrained_layout=True))
        self.plotLayout.addWidget(self.canvas)

        self.init_empty_plot()

    # ---------------------------------------------------------------------
    # DATA HANDLING
    # ---------------------------------------------------------------------

    def populate_layers(self):
        self.layerCombo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if hasattr(layer, "fields"):
                self.layerCombo.addItem(layer.name(), layer)
        self.populate_fields()

    def populate_fields(self):
        self.xFieldCombo.clear()
        self.yFieldsList.clear()
        self.y2FieldCombo.clear()

        layer = self.layerCombo.currentData()
        if not layer:
            return

        # Check selected features if needed
        if self.selectedOnlyCheck.isChecked():
            if layer.selectedFeatureCount() == 0:
                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr(
                        "You enabled 'Use selected features only', "
                        "but no features are currently selected."
                    )
                )
                return

        for field in layer.fields():
            name = field.name()
            self.xFieldCombo.addItem(name)
            self.yFieldsList.addItem(name)
            self.y2FieldCombo.addItem(name)

    def get_features(self):
        layer = self.layerCombo.currentData()
        if not layer:
            return []

        if self.selectedOnlyCheck.isChecked():
            return layer.selectedFeatures()
        else:
            return list(layer.getFeatures())

    def get_field_type(self, field: QgsField):
        if field.isNumeric():
            return "numeric"
        if field.type() in (QVariant.Date, QVariant.DateTime, QVariant.Time):
            return "date"
        if field.type() == QVariant.String:
            return "string"
        return "other"

    def get_data(self, field_name):
        layer = self.layerCombo.currentData()
        if not layer:
            return [], "other"

        field_index = layer.fields().indexOf(field_name)
        if field_index < 0:
            return [], "other"

        field = layer.fields()[field_index]
        ftype = self.get_field_type(field)

        values = []
        for f in self.get_features():
            val = f[field_name]
            if val is None:
                continue

            if ftype == "date":
                if isinstance(val, (datetime.date, datetime.datetime)):
                    values.append(val)
                else:
                    try:
                        values.append(datetime.datetime.fromisoformat(str(val)))
                    except Exception:
                        continue
            else:
                values.append(val)

        return values, ftype

    # ---------------------------------------------------------------------
    # SMART CHART TYPE SUGGESTION
    # ---------------------------------------------------------------------

    def suggest_chart_type(self, x_type, y_types):
        if x_type == "string" and all(t == "numeric" for t in y_types):
            return "Bar"
        if x_type == "date" and all(t == "numeric" for t in y_types):
            return "Line"
        if x_type == "numeric" and all(t == "numeric" for t in y_types):
            return "Scatter"
        return "Histogram"

    def on_chart_type_changed(self):
        chart_type = self.chartTypeCombo.currentText()
        self.binSpin.setEnabled(chart_type == "Histogram")

        if self.separateSubplotsCheck.isChecked():
            if chart_type in ("Bar", "Pie", "Boxplot"):
                QMessageBox.information(
                    self,
                    self.tr("Suggestion"),
                    self.tr(
                        "The option 'Separate subplot for each Y' is not recommended for "
                        "Bar, Pie or Boxplot charts.\n\n"
                        "These chart types are designed to show multiple series on the same axis.\n\n"
                        "Use subplots when Y series have very different scales or when you want "
                        "to compare trends without overlapping."
                    )
                )

    def on_subplot_option_changed(self):
        if self.separateSubplotsCheck.isChecked():
            chart_type = self.chartTypeCombo.currentText()
            if chart_type in ("Bar", "Pie", "Boxplot"):
                QMessageBox.information(
                    self,
                    self.tr("Suggestion"),
                    self.tr(
                        "Separate subplots are not recommended for this chart type.\n"
                        "Consider whether you really need them."
                    )
                )

    def toggle_y2_title(self):
        self.y2AxisTitleEdit.setEnabled(self.enableY2Check.isChecked())

    # ---------------------------------------------------------------------
    # MAIN PLOT ENTRY POINT
    # ---------------------------------------------------------------------

    def plot(self):
        layer = self.layerCombo.currentData()
        if not layer:
            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr("No layer selected.")
            )
            return

        x_field = self.xFieldCombo.currentText()
        if not x_field:
            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr("Please select an X field.")
            )
            return

        selected_items = self.yFieldsList.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr("Please select at least one Y field.")
            )
            return

        y_fields = [item.text() for item in selected_items]

        # X data
        x_data, x_type = self.get_data(x_field)
        if not x_data:
            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr("No valid data for X field: {0}").format(x_field)
            )
            return

        # Y data
        y_data_list = []
        y_types = []
        for yf in y_fields:
            data, ftype = self.get_data(yf)
            if not data:
                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr("No valid data for Y field: {0}").format(yf)
                )
                return
            y_data_list.append(data)
            y_types.append(ftype)

        # Optional Y2
        use_y2 = self.enableY2Check.isChecked()
        y2_field = None
        y2_data = None
        y2_type = None
        if use_y2:
            y2_field = self.y2FieldCombo.currentText()
            y2_data, y2_type = self.get_data(y2_field)
            if not y2_data:
                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr("No valid data for Y2 field: {0}").format(y2_field)
                )
                return

        # Auto chart type suggestion
        if self.autoChartCheck.isChecked():
            suggested = self.suggest_chart_type(x_type, y_types)
            index = self.chartTypeCombo.findText(suggested)
            if index >= 0:
                self.chartTypeCombo.setCurrentIndex(index)

        chart_type = self.chartTypeCombo.currentText()

        # Histogram bins suggestion
        if chart_type == "Histogram":
            self._suggest_bins(y_data_list[0])

        fig = self.canvas.figure
        fig.clear()

        separate_subplots = self.separateSubplotsCheck.isChecked()
        n_series = len(y_fields)

        # Colors and styles
        base_color = self.colorWidgetY.color().name()
        bg_color = self.colorWidgetBg.color().name()
        marker = self.markerCombo.currentText()
        linestyle = self.lineStyleCombo.currentText()
        bins = self.binSpin.value()

        color_y2 = self.colorWidgetY2.color().name()
        marker_y2 = self.markerY2Combo.currentText()
        linestyle_y2 = self.lineStyleY2Combo.currentText()

        # Build color cycle for multiple Y series
        default_cycle = plt.rcParams.get("axes.prop_cycle", None)
        if default_cycle is not None:
            cycle_colors = list(default_cycle.by_key().get("color", []))
        else:
            cycle_colors = []

        # Fallback: at least one color
        if not cycle_colors:
            cycle_colors = [base_color]

        # Force first color = user-selected Y Color
        cycle_colors[0] = base_color

        # Final list of colors
        colors = cycle_colors

        # Titles
        main_title = self.mainTitleEdit.text().strip()
        x_title = self.xAxisTitleEdit.text().strip()
        y_title = self.yAxisTitleEdit.text().strip()
        y2_title = self.y2AxisTitleEdit.text().strip()

        # Axes / subplots
        if separate_subplots and n_series > 1 and chart_type not in ("Pie", "Boxplot", "Radar"):
            axes = []
            for i in range(n_series):
                ax = fig.add_subplot(n_series, 1, i + 1)
                axes.append(ax)
        else:
            axes = [fig.add_subplot(111)]

        ax2 = None
        if use_y2:
            if chart_type in ("Line", "Scatter", "Linear Regression", "Curve Fitting"):
                ax2 = axes[0].twinx()
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr("Y2 axis is only supported for Line, Scatter, Linear Regression and Curve Fitting.")
                )
                return

        # Dispatch to specific plot handlers
        self._plot_dispatch(
            fig=fig,
            axes=axes,
            ax2=ax2,
            chart_type=chart_type,
            x_data=x_data,
            x_field=x_field,
            y_fields=y_fields,
            y_data_list=y_data_list,
            y2_field=y2_field,
            y2_data=y2_data,
            separate_subplots=separate_subplots,
            colors=colors,
            color_y2=color_y2,
            bg_color=bg_color,
            marker=marker,
            linestyle=linestyle,
            marker_y2=marker_y2,
            linestyle_y2=linestyle_y2,
            bins=bins
        )

        # Axis titles
        axes[0].set_xlabel(
            x_title if x_title else x_field,
            fontweight="bold"
        )
        axes[0].set_ylabel(
            y_title if y_title else self.tr("Value"),
            fontweight="bold"
        )

        if use_y2 and ax2:
            ax2.set_ylabel(
                y2_title if y2_title else (y2_field or self.tr("Y2")),
                fontweight="bold"
            )

        # Main title
        fig.suptitle(
            main_title if main_title else "{0} - {1}".format(chart_type, layer.name()),
            fontweight="bold"
        )

        # Legend
        if self.legendCheck.isChecked() and chart_type not in ("Pie", "Boxplot", "Radar"):
            handles1, labels1 = axes[0].get_legend_handles_labels()
            if use_y2 and ax2:
                handles2, labels2 = ax2.get_legend_handles_labels()
                axes[0].legend(handles1 + handles2, labels1 + labels2)
            else:
                axes[0].legend(handles1, labels1)

        self.canvas.draw()

    # ---------------------------------------------------------------------
    # BINS SUGGESTION FOR HISTOGRAM
    # ---------------------------------------------------------------------

    def _suggest_bins(self, y_values):
        n = len(y_values)
        if n < 2:
            return

        y_sorted = sorted(y_values)
        q1 = y_sorted[int(0.25 * n)]
        q3 = y_sorted[int(0.75 * n)]
        iqr = q3 - q1 if q3 > q1 else 1

        bin_width = 2 * iqr * (n ** (-1 / 3))
        if bin_width <= 0:
            bins_optimal = max(5, int(n ** 0.5))
        else:
            bins_optimal = max(3, int((max(y_values) - min(y_values)) / bin_width))

        bins_user = self.binSpin.value()

        if bins_user > bins_optimal * 2:
            QMessageBox.information(
                self,
                self.tr("Bins suggestion"),
                self.tr(
                    "You set {0} bins, but the recommended value is about {1}.\n\n"
                    "Too many bins make the histogram noisy and hard to read."
                ).format(bins_user, bins_optimal)
            )

        if bins_user < bins_optimal / 2:
            QMessageBox.information(
                self,
                self.tr("Bins suggestion"),
                self.tr(
                    "You set only {0} bins, but the recommended value is about {1}.\n\n"
                    "Too few bins make the histogram oversimplified."
                ).format(bins_user, bins_optimal)
            )

    # ---------------------------------------------------------------------
    # DISPATCH TO SPECIFIC PLOT TYPES
    # ---------------------------------------------------------------------

    def _plot_dispatch(
        self,
        fig,
        axes,
        ax2,
        chart_type,
        x_data,
        x_field,
        y_fields,
        y_data_list,
        y2_field,
        y2_data,
        separate_subplots,
        colors,    
        color_y2,
        bg_color,
        marker,
        linestyle,
        marker_y2,
        linestyle_y2,
        bins
    ):


        n_series = len(y_fields)

        # Radar is special: uses polar axes and averages
        if chart_type == "Radar":
            fig.clear()
            self._plot_radar(fig, y_data_list, y_fields)
            self.canvas.draw()
            return

        for idx, (yf, y_data) in enumerate(zip(y_fields, y_data_list)):
            if separate_subplots and n_series > 1 and chart_type not in ("Pie", "Boxplot"):
                ax = axes[idx]
            else:
                ax = axes[0]

            # Pick color for this series
            series_color = colors[idx % len(colors)]

            if chart_type == "Line":
                self._plot_line(ax, x_data, y_data, yf, series_color, marker, linestyle)

            elif chart_type == "Scatter":
                self._plot_scatter(ax, x_data, y_data, yf, series_color, marker)

            elif chart_type == "Bar":
                self._plot_bar(ax, x_data, y_data, yf, series_color)

            elif chart_type == "Histogram":
                self._plot_histogram(ax, y_data, yf, series_color, bins)

            elif chart_type == "Pie":
                if n_series > 1:
                    QMessageBox.warning(
                        self,
                        self.tr("Advanced Charts"),
                        self.tr("Pie chart supports only one Y field at a time.")
                    )
                    fig.clear()
                    self.canvas.draw()
                    return
                self._plot_pie(ax, x_data, y_data)
                break

            elif chart_type == "Boxplot":
                self._plot_boxplot(ax, y_data_list, y_fields)
                break

            elif chart_type == "Area":
                self._plot_area(ax, x_data, y_data_list, y_fields)
                break

            elif chart_type == "Violin":
                self._plot_violin(ax, y_data_list, y_fields, series_color)
                break

            elif chart_type == "Linear Regression":
                self._plot_line(ax, x_data, y_data, yf, series_color, marker, linestyle)
                if self.enableLinearRegressionCheck.isChecked():
                    self._plot_linear_regression(ax, x_data, y_data, series_color)

            elif chart_type == "Curve Fitting":
                self._plot_line(ax, x_data, y_data, yf, series_color, marker, linestyle)
                fit_type = self.fitTypeCombo.currentText()
                degree = self.polyDegreeSpin.value()
                self._plot_curve_fit(ax, x_data, y_data, fit_type, degree, series_color)

            ax.set_facecolor(bg_color)
            if self.gridCheck.isChecked():
                ax.grid(True)


        # Y2 plotting
        if ax2 and y2_data is not None and chart_type in ("Line", "Scatter", "Linear Regression", "Curve Fitting"):
            if chart_type in ("Line", "Linear Regression", "Curve Fitting"):
                self._plot_line(
                    ax2,
                    x_data,
                    y2_data,
                    y2_field,
                    color_y2,
                    marker_y2,
                    linestyle_y2
                )
            elif chart_type == "Scatter":
                self._plot_scatter(
                    ax2,
                    x_data,
                    y2_data,
                    y2_field,
                    color_y2,
                    marker_y2
                )
            ax2.grid(False)

    # ---------------------------------------------------------------------
    # BASIC PLOT ENGINES
    # ---------------------------------------------------------------------

    def _plot_line(self, ax, x_data, y_data, label, color, marker, linestyle):
        ax.plot(
            x_data,
            y_data,
            color=color,
            marker=None if marker == "None" else marker,
            linestyle=None if linestyle == "None" else linestyle,
            label=label
        )

    def _plot_scatter(self, ax, x_data, y_data, label, color, marker):
        ax.scatter(
            x_data,
            y_data,
            color=color,
            marker=None if marker == "None" else marker,
            label=label
        )

    def _plot_bar(self, ax, x_data, y_data, label, color):
        ax.bar(
            x_data,
            y_data,
            color=color,
            label=label
        )

    def _plot_histogram(self, ax, y_data, label, color, bins):
        ax.hist(
            y_data,
            bins=bins,
            color=color,
            alpha=0.7,
            edgecolor="black",
            linewidth=1.0,
            label=label
        )

    def _plot_pie(self, ax, x_data, y_data):
        ax.pie(
            y_data,
            labels=x_data,
            autopct='%1.1f%%'
        )
        ax.set_aspect('equal')

        # Hide axes for pie chart
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False
        )

    def _plot_boxplot(self, ax, y_data_list, y_fields):
        if len(y_data_list) == 1:
            ax.boxplot(y_data_list[0], labels=[y_fields[0]])
        else:
            ax.boxplot(y_data_list, labels=y_fields)

    def _plot_area(self, ax, x_data, y_data_list, y_fields):
        import numpy as np

        X = np.array(x_data)
        Y = np.vstack([np.array(y) for y in y_data_list])

        ax.stackplot(X, Y, labels=y_fields)

    # ---------------------------------------------------------------------
    # ADVANCED PLOT ENGINES
    # ---------------------------------------------------------------------

    def _plot_violin(self, ax, y_data_list, y_fields, color):
        """
        Violin plot for one or multiple Y fields.
        """
        parts = ax.violinplot(
            y_data_list,
            showmeans=True,
            showmedians=True
        )

        # Color bodies
        for pc in parts['bodies']:
            pc.set_facecolor(color)
            pc.set_edgecolor("black")
            pc.set_alpha(0.7)

        # Color lines
        for key in ('cbars', 'cmins', 'cmaxes', 'cmeans', 'cmedians'):
            if key in parts:
                parts[key].set_color("black")

        ax.set_xticks(range(1, len(y_fields) + 1))
        ax.set_xticklabels(y_fields)

    def _plot_radar(self, fig, y_data_list, y_fields):
        """
        Radar plot: uses mean values of each Y field.
        """
        import numpy as np

        categories = y_fields
        N = len(categories)

        # Compute mean for each Y field
        values = np.array([np.mean(y) for y in y_data_list])
        values = np.append(values, values[0])  # close the loop

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
        angles = np.append(angles, angles[0])

        ax = fig.add_subplot(111, polar=True)

        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

    # ---------------------------------------------------------------------
    # LINEAR REGRESSION
    # ---------------------------------------------------------------------

    def _plot_linear_regression(self, ax, x_data, y_data, color):
        import numpy as np
        import datetime

        # Convert X to numeric
        x_numeric = []
        for v in x_data:
            if isinstance(v, (datetime.date, datetime.datetime)):
                x_numeric.append(v.toordinal())
            else:
                try:
                    x_numeric.append(float(v))
                except:
                    return  # cannot regress

        x = np.array(x_numeric, dtype=float)
        y = np.array(y_data, dtype=float)

        # Normalize X to avoid overflow
        x0 = x.mean()
        x_norm = x - x0

        # Fit
        m, b = np.polyfit(x_norm, y, 1)

        # Generate fit line
        x_fit = np.linspace(x_norm.min(), x_norm.max(), 200)
        y_fit = m * x_fit + b

        # Denormalize X for plotting
        x_fit_plot = x_fit + x0

        ax.plot(
            x_fit_plot,
            y_fit,
            color=color,
            linestyle="--",
            linewidth=2,
            label=self.tr("Linear regression")
        )


    # ---------------------------------------------------------------------
    # CURVE FITTING (Polynomial, Exponential, Logarithmic, Power)
    # ---------------------------------------------------------------------

    def _plot_curve_fit(self, ax, x_data, y_data, fit_type, degree, color):
        """
        Curve fitting using scipy.optimize.curve_fit when needed.
        Polynomial uses numpy.polyfit.
        """
        import numpy as np

        try:
            from scipy.optimize import curve_fit
        except ImportError:
            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr(
                    "SciPy is required for curve fitting (except polynomial). "
                    "Please install SciPy or use Polynomial fitting."
                )
            )
            return

        x = np.array(x_data, dtype=float)
        y = np.array(y_data, dtype=float)

        # Polynomial fit
        if fit_type == "Polynomial":
            coeffs = np.polyfit(x, y, degree)
            poly = np.poly1d(coeffs)
            x_fit = np.linspace(min(x), max(x), 200)
            y_fit = poly(x_fit)

        # Exponential fit
        elif fit_type == "Exponential":
            def f(x, a, b):
                return a * np.exp(b * x)
            params, _ = curve_fit(f, x, y)
            x_fit = np.linspace(min(x), max(x), 200)
            y_fit = f(x_fit, *params)

        # Logarithmic fit
        elif fit_type == "Logarithmic":
            def f(x, a, b):
                return a + b * np.log(x)
            params, _ = curve_fit(f, x, y)
            x_fit = np.linspace(min(x), max(x), 200)
            y_fit = f(x_fit, *params)

        # Power fit
        elif fit_type == "Power":
            def f(x, a, b):
                return a * x ** b
            params, _ = curve_fit(f, x, y)
            x_fit = np.linspace(min(x), max(x), 200)
            y_fit = f(x_fit, *params)

        else:
            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr("Unknown fit type.")
            )
            return

        ax.plot(
            x_fit,
            y_fit,
            color=color,
            linestyle="--",
            linewidth=2,
            label=self.tr("{0} fit").format(fit_type)
        )

    # ---------------------------------------------------------------------
    # SAVE PLOT
    # ---------------------------------------------------------------------

    def save_plot(self):
        """
        Save the current figure as PNG, JPG or PDF.
        """
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save chart"),
            "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )

        if path:
            try:
                self.canvas.figure.savefig(path, dpi=300)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr("Error saving image:\n{0}").format(str(e))
                )

    # ---------------------------------------------------------------------
    # OPTIONAL UTILITIES
    # ---------------------------------------------------------------------

    def _safe_float_list(self, values):
        """
        Convert a list of values to float when possible.
        """
        out = []
        for v in values:
            try:
                out.append(float(v))
            except Exception:
                pass
        return out

    def _safe_numeric(self, value):
        """
        Convert a single value to float if possible.
        """
        try:
            return float(value)
        except Exception:
            return None
